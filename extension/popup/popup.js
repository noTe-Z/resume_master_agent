document.addEventListener('DOMContentLoaded', async () => {
    const jobList = document.getElementById('jobList');
    
    // Add event listener for "View All Jobs" button
    document.getElementById('viewAllJobs').addEventListener('click', () => {
        chrome.tabs.create({ url: chrome.runtime.getURL('popup/jobs.html') });
    });
    
    // Update daily goal progress
    await updateDailyGoal();
    
    try {
        const response = await fetch('http://localhost:3000/get-jobs');
        const data = await response.json();
        
        if (data.length === 0) {
            jobList.innerHTML = '<p class="no-jobs">No saved jobs yet.</p>';
            return;
        }
        
        jobList.innerHTML = data.map(job => `
            <div class="job-card">
                <div class="job-header">
                    <h3 class="job-title">${job.title}</h3>
                    ${job.company ? `<p class="company-name">${job.company}</p>` : ''}
                </div>
                ${job.description ? `
                    <div class="job-description">
                        <p>${job.description.substring(0, 200)}${job.description.length > 200 ? '...' : ''}</p>
                    </div>
                ` : ''}
                <div class="job-actions">
                    ${job.apply_link ? `
                        <a href="${job.apply_link}" target="_blank" class="action-button apply">Apply Now</a>
                    ` : ''}
                    <button class="action-button delete" data-job-id="${job.id}">Delete</button>
                </div>
                <div class="job-meta">
                    <span class="saved-time">Saved: ${new Date(job.saved_at).toLocaleString()}</span>
                </div>
            </div>
        `).join('');
        
        // Add event listeners for delete buttons
        document.querySelectorAll('.delete').forEach(button => {
            button.addEventListener('click', async () => {
                try {
                    const jobId = button.dataset.jobId;
                    const response = await fetch(`http://localhost:3000/delete-job/${jobId}`, {
                        method: 'DELETE'
                    });
                    
                    if (response.ok) {
                        button.closest('.job-card').remove();
                        if (jobList.children.length === 0) {
                            jobList.innerHTML = '<p class="no-jobs">No saved jobs yet.</p>';
                        }
                        // Update goal progress after deletion
                        await updateDailyGoal();
                    } else {
                        throw new Error('Failed to delete job');
                    }
                } catch (error) {
                    console.error('Error deleting job:', error);
                    button.textContent = 'Error!';
                    setTimeout(() => {
                        button.textContent = 'Delete';
                    }, 2000);
                }
            });
        });
        
    } catch (error) {
        console.error('Error fetching jobs:', error);
        jobList.innerHTML = '<p class="error">Failed to load saved jobs.</p>';
    }
});

async function updateDailyGoal() {
    try {
        const response = await fetch('http://localhost:3000/jobs/today-stats');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const stats = await response.json();
        
        // Update progress count
        document.getElementById('todayProgress').textContent = stats.today_applied;
        
        // Update status message
        const goalStatus = document.getElementById('goalStatus');
        if (stats.goal_met) {
            goalStatus.textContent = '🎉 Daily goal achieved!';
            goalStatus.className = 'goal-status met';
        } else {
            const remaining = stats.daily_goal - stats.today_applied;
            goalStatus.textContent = `${remaining} more to reach today's goal`;
            goalStatus.className = 'goal-status not-met';
        }
    } catch (error) {
        console.error('Error updating daily goal:', error);
        document.getElementById('goalStatus').textContent = 'Error loading goal progress';
    }
} 