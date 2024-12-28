document.addEventListener('DOMContentLoaded', () => {
    loadSavedJobs();
    updateJobStats();
});

async function updateJobStats() {
    try {
        const response = await fetch('http://localhost:3000/jobs/stats');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const stats = await response.json();
        
        // Update stats display
        document.getElementById('totalJobs').textContent = stats.total || 0;
        document.getElementById('appliedJobs').textContent = stats.by_status?.applied || 0;
        document.getElementById('toApplyJobs').textContent = stats.by_status?.to_apply || 0;
        document.getElementById('interviewingJobs').textContent = stats.by_status?.interviewing || 0;
    } catch (error) {
        console.error('Error loading job stats:', error);
    }
}

async function loadSavedJobs() {
    try {
        const response = await fetch('http://localhost:3000/jobs');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const jobs = await response.json();
        
        const tableBody = document.getElementById('jobsTableBody');
        const noJobsDiv = document.getElementById('noJobs');
        
        if (!Array.isArray(jobs) || jobs.length === 0) {
            tableBody.innerHTML = '';
            noJobsDiv.classList.remove('hidden');
            return;
        }

        noJobsDiv.classList.add('hidden');
        tableBody.innerHTML = jobs.map(job => createJobRow(job)).join('');
        
        // Add event listeners for status changes
        document.querySelectorAll('.status-select').forEach(select => {
            select.addEventListener('change', handleStatusChange);
            // Store the initial value for rollback if update fails
            select.setAttribute('data-previous-value', select.value);
        });
    } catch (error) {
        console.error('Error loading jobs:', error);
        document.getElementById('noJobs').textContent = 'Error loading jobs. Please try again.';
        document.getElementById('noJobs').classList.remove('hidden');
    }
}

function createJobRow(job) {
    // Ensure all required properties exist with default values
    const safeJob = {
        id: job.id || '',
        company: job.company || '',
        title: job.title || '',
        apply_link: job.apply_link || '#',
        status: job.status || 'to_apply'
    };

    return `
        <tr data-job-id="${escapeHtml(safeJob.id)}">
            <td>${escapeHtml(safeJob.company)}</td>
            <td>${escapeHtml(safeJob.title)}</td>
            <td>
                ${safeJob.apply_link !== '#' ? `
                    <a href="${escapeHtml(safeJob.apply_link)}" 
                       target="_blank" 
                       class="apply-button">
                        Apply
                    </a>
                ` : '<span class="no-link">No link available</span>'}
            </td>
            <td>
                <select class="status-select" data-job-id="${escapeHtml(safeJob.id)}">
                    <option value="to_apply" ${safeJob.status === 'to_apply' ? 'selected' : ''}>To Apply</option>
                    <option value="applied" ${safeJob.status === 'applied' ? 'selected' : ''}>Applied</option>
                    <option value="interviewing" ${safeJob.status === 'interviewing' ? 'selected' : ''}>Interviewing</option>
                </select>
            </td>
        </tr>
    `;
}

async function handleStatusChange(event) {
    const select = event.target;
    const jobId = select.dataset.jobId;
    const newStatus = select.value;
    const previousValue = select.getAttribute('data-previous-value');
    
    try {
        const response = await fetch(`http://localhost:3000/jobs/${jobId}/status`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ status: newStatus })
        });
        
        if (!response.ok) {
            throw new Error('Failed to update status');
        }
        
        // Update the previous value for future rollbacks
        select.setAttribute('data-previous-value', newStatus);
        
        // Add visual feedback
        const row = select.closest('tr');
        row.style.backgroundColor = '#e6ffe6';
        setTimeout(() => {
            row.style.backgroundColor = '';
        }, 500);

        // Update the stats after status change
        await updateJobStats();
    } catch (error) {
        console.error('Error updating job status:', error);
        // Reset the select to its previous value
        select.value = previousValue;
        alert('Failed to update job status. Please try again.');
    }
}

function escapeHtml(unsafe) {
    if (unsafe === null || unsafe === undefined) {
        return '';
    }
    return String(unsafe)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
} 