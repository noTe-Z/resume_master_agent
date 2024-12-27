document.addEventListener('DOMContentLoaded', async () => {
    const jobList = document.getElementById('jobList');
    
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