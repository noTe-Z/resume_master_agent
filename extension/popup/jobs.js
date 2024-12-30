document.addEventListener('DOMContentLoaded', loadJobs);

async function loadJobs() {
    try {
        console.log('Loading jobs...');
        const response = await fetch('http://localhost:3000/jobs');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const jobs = await response.json();
        console.log('Jobs loaded:', jobs);
        
        const tableBody = document.getElementById('jobsTableBody');
        const noJobsDiv = document.getElementById('noJobs');
        
        // Clear existing content
        tableBody.innerHTML = '';
        
        if (jobs.length === 0) {
            console.log('No jobs found');
            noJobsDiv.classList.remove('hidden');
            return;
        }
        
        noJobsDiv.classList.add('hidden');
        jobs.forEach(job => {
            const row = createJobRow(job);
            tableBody.appendChild(row);
        });
        
        // Add event listeners for status selects
        document.querySelectorAll('.status-select').forEach(select => {
            select.addEventListener('change', handleStatusChange);
            // Store the initial value for rollback
            select.setAttribute('data-previous-value', select.value);
        });
        
        await updateJobStats();
        console.log('Jobs loaded successfully');
        
    } catch (error) {
        console.error('Error loading jobs:', error);
        const tableBody = document.getElementById('jobsTableBody');
        tableBody.innerHTML = `<tr><td colspan="5">Error loading jobs: ${error.message}</td></tr>`;
    }
}

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

function createJobRow(job) {
    // Ensure all required properties exist with default values
    const safeJob = {
        id: job.id || '',
        company: job.company || '',
        title: job.title || '',
        apply_link: job.apply_link || '#',
        status: job.status || 'to_apply',
        has_tailored_resume: job.has_tailored_resume || false
    };

    const resumeButton = safeJob.has_tailored_resume ? `
        <a href="tailored-resume.html?jobId=${escapeHtml(safeJob.id)}" 
           target="_blank" 
           class="resume-button tailored">
            Tailored Resume
        </a>
    ` : `
        <button class="resume-button" 
                data-job-id="${escapeHtml(safeJob.id)}">
            Tailor Resume
        </button>
    `;

    const row = document.createElement('tr');
    row.dataset.jobId = safeJob.id;
    row.innerHTML = `
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
        <td>${resumeButton}</td>
    `;

    // Add event listener for the resume button if it's not already tailored
    if (!safeJob.has_tailored_resume) {
        const button = row.querySelector('.resume-button');
        button.addEventListener('click', () => tailorResume(safeJob.id));
    }

    return row;
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

async function tailorResume(jobId) {
    try {
        const button = document.querySelector(`tr[data-job-id="${jobId}"] .resume-button`);
        button.disabled = true;
        button.textContent = 'Tailoring...';

        const response = await fetch(`http://localhost:3000/jobs/${jobId}/tailor-resume`, {
            method: 'POST'
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        if (!data.job || !data.job.has_tailored_resume) {
            throw new Error('Resume was not created successfully');
        }

        // Update button to show success and link to tailored resume
        const row = document.querySelector(`tr[data-job-id="${jobId}"]`);
        const cell = row.querySelector('td:last-child');
        cell.innerHTML = `
            <a href="tailored-resume.html?jobId=${escapeHtml(jobId)}" 
               target="_blank" 
               class="resume-button tailored">
                Tailored Resume
            </a>
        `;

        // Add visual feedback
        row.style.backgroundColor = '#e6ffe6';
        setTimeout(() => {
            row.style.backgroundColor = '';
        }, 500);

    } catch (error) {
        console.error('Error tailoring resume:', error);
        const button = document.querySelector(`tr[data-job-id="${jobId}"] .resume-button`);
        button.disabled = false;
        button.textContent = 'Tailor Resume';
        alert('Failed to tailor resume. Please try again.');
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