document.addEventListener('DOMContentLoaded', () => {
    // Load jobs on page load
    loadJobs();
    
    // Set up resume upload functionality
    setupResumeUpload();
});

// Resume upload and parsing functionality
function setupResumeUpload() {
    const uploadButton = document.getElementById('uploadResumeBtn');
    const parseButton = document.getElementById('parseResumeBtn');
    const fileInput = document.getElementById('resumeFileInput');
    const fileNameSpan = document.getElementById('selectedFileName');
    const modal = document.getElementById('parsedResumeModal');
    const closeButton = modal.querySelector('.close');
    const parsedContent = document.getElementById('parsedResumeContent');
    
    // Show file input when upload button is clicked
    uploadButton.addEventListener('click', () => {
        fileInput.click();
    });
    
    // Handle file selection
    fileInput.addEventListener('change', (event) => {
        if (event.target.files.length > 0) {
            const file = event.target.files[0];
            fileNameSpan.textContent = file.name;
            parseButton.style.display = 'inline-block';
        } else {
            fileNameSpan.textContent = '';
            parseButton.style.display = 'none';
        }
    });
    
    // Parse resume when parse button is clicked
    parseButton.addEventListener('click', async () => {
        console.log('Parse Resume button clicked');
        if (fileInput.files.length === 0) {
            alert('Please select a resume file first.');
            return;
        }
        
        const file = fileInput.files[0];
        console.log(`Selected file: ${file.name}, type: ${file.type}, size: ${file.size} bytes`);
        parseButton.disabled = true;
        parseButton.textContent = 'Parsing...';
        
        try {
            console.log('Starting resume parsing...');
            const parsedData = await parseResume(file);
            console.log('Resume parsed successfully:', parsedData);
            displayParsedResume(parsedData);
        } catch (error) {
            console.error('Error parsing resume:', error);
            alert('Failed to parse resume: ' + (error.message || 'Unknown error'));
        } finally {
            parseButton.disabled = false;
            parseButton.textContent = 'Parse Resume';
            console.log('Parse button reset');
        }
    });
    
    // Close modal when close button is clicked
    closeButton.addEventListener('click', () => {
        modal.style.display = 'none';
    });
    
    // Close modal when clicking outside of it
    window.addEventListener('click', (event) => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
}

// Function to parse the resume by sending it to the backend
async function parseResume(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    console.log('Sending resume file to server:', file.name);
    
    try {
        const response = await fetch('/parse-resume', {
            method: 'POST',
            body: formData
        });
        
        const responseData = await response.json();
        
        if (!response.ok) {
            throw new Error(responseData.error || 'Failed to parse resume');
        }
        
        console.log('Resume parsing response:', responseData);
        return responseData;
    } catch (error) {
        console.error('Error in parseResume function:', error);
        throw error;
    }
}

// Function to display the parsed resume in the modal
function displayParsedResume(data) {
    const modal = document.getElementById('parsedResumeModal');
    const parsedContent = document.getElementById('parsedResumeContent');
    const parserType = document.getElementById('parserType');
    
    // Display which parser was used
    if (data.message && data.message.includes('enhanced parser')) {
        parserType.textContent = 'Enhanced Parser';
        parserType.className = 'parser-badge enhanced';
    } else {
        parserType.textContent = 'Standard Parser';
        parserType.className = 'parser-badge standard';
    }
    
    // Format the parsed content nicely
    let formattedContent = '';
    
    // Check if we have valid data
    if (!data.data || typeof data.data !== 'object') {
        formattedContent = 'Error: Invalid resume data format returned from server.';
        parsedContent.textContent = formattedContent;
        modal.style.display = 'block';
        return;
    }
    
    // Contact Information
    formattedContent += '=== CONTACT INFORMATION ===\n';
    if (data.data.contact_info && typeof data.data.contact_info === 'object') {
        for (const [key, value] of Object.entries(data.data.contact_info)) {
            if (value) {
                formattedContent += `${key.replace(/_/g, ' ').toUpperCase()}: ${value}\n`;
            }
        }
    } else {
        formattedContent += 'No contact information found.\n';
    }
    
    // Summary
    formattedContent += '\n=== SUMMARY ===\n';
    formattedContent += data.data.summary || 'No summary found.\n';
    
    // Work Experience
    formattedContent += '\n=== WORK EXPERIENCE ===\n';
    if (data.data.experiences && Array.isArray(data.data.experiences) && data.data.experiences.length > 0) {
        data.data.experiences.forEach((exp, index) => {
            formattedContent += `\n[Experience ${index + 1}]\n`;
            formattedContent += `Company: ${exp.company || 'N/A'}\n`;
            formattedContent += `Position: ${exp.position || 'N/A'}\n`;
            if (exp.location) {
                formattedContent += `Location: ${exp.location}\n`;
            }
            formattedContent += `Start Date: ${exp.start_date || 'N/A'}\n`;
            formattedContent += `End Date: ${exp.end_date || 'N/A'}\n`;
            
            if (exp.responsibilities && Array.isArray(exp.responsibilities) && exp.responsibilities.length > 0) {
                formattedContent += '\nResponsibilities:\n';
                exp.responsibilities.forEach(resp => {
                    formattedContent += `  • ${resp}\n`;
                });
            }
        });
    } else {
        formattedContent += 'No work experience found.\n';
    }
    
    // Education
    formattedContent += '\n=== EDUCATION ===\n';
    if (typeof data.data.education === 'string') {
        // Handle education as string
        formattedContent += data.data.education;
    } else if (Array.isArray(data.data.education) && data.data.education.length > 0) {
        // Handle education as array of objects
        data.data.education.forEach((edu, index) => {
            formattedContent += `\n[Education ${index + 1}]\n`;
            formattedContent += `Degree: ${edu.degree || 'N/A'}\n`;
            formattedContent += `Institution: ${edu.institution || 'N/A'}\n`;
            if (edu.start_date) formattedContent += `Start Date: ${edu.start_date}\n`;
            if (edu.end_date) formattedContent += `End Date: ${edu.end_date}\n`;
            
            if (edu.details && Array.isArray(edu.details) && edu.details.length > 0) {
                formattedContent += '\nDetails:\n';
                edu.details.forEach(detail => {
                    formattedContent += `  • ${detail}\n`;
                });
            }
        });
    } else {
        formattedContent += 'No education found.\n';
    }
    
    // Skills
    formattedContent += '\n=== SKILLS ===\n';
    if (data.data.skills) {
        if (typeof data.data.skills === 'string') {
            formattedContent += data.data.skills;
        } else if (typeof data.data.skills === 'object') {
            for (const [category, skills] of Object.entries(data.data.skills)) {
                if (skills && Array.isArray(skills) && skills.length > 0) {
                    formattedContent += `\n${category.replace(/_/g, ' ').toUpperCase()}:\n`;
                    skills.forEach(skill => {
                        formattedContent += `  • ${skill}\n`;
                    });
                }
            }
        }
    } else {
        formattedContent += 'No skills found.\n';
    }
    
    // Research Experience (from enhanced parser)
    if (data.data.research && Array.isArray(data.data.research) && data.data.research.length > 0) {
        formattedContent += '\n=== RESEARCH EXPERIENCE ===\n';
        data.data.research.forEach((research, index) => {
            formattedContent += `\n[Research ${index + 1}]\n`;
            if (research.title) formattedContent += `Title: ${research.title}\n`;
            if (research.institution) formattedContent += `Institution: ${research.institution}\n`;
            if (research.start_date) formattedContent += `Start Date: ${research.start_date}\n`;
            if (research.end_date) formattedContent += `End Date: ${research.end_date}\n`;
            
            if (research.description && Array.isArray(research.description) && research.description.length > 0) {
                formattedContent += '\nDescription:\n';
                research.description.forEach(desc => {
                    formattedContent += `  • ${desc}\n`;
                });
            }
        });
    }
    
    // Certifications
    if (data.data.certifications && Array.isArray(data.data.certifications) && data.data.certifications.length > 0) {
        formattedContent += '\n=== CERTIFICATIONS ===\n';
        data.data.certifications.forEach((cert, index) => {
            formattedContent += `  ${index + 1}. ${cert}\n`;
        });
    }
    
    // Set the content and show the modal
    parsedContent.textContent = formattedContent;
    modal.style.display = 'block';
}

async function loadJobs() {
    try {
        console.log('Loading jobs...');
        const response = await fetch('/jobs');
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
        const response = await fetch('/jobs/stats');
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
        select.disabled = true;
        const response = await fetch(`/jobs/${jobId}/status`, {
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
    } finally {
        select.disabled = false;
    }
}

async function tailorResume(jobId) {
    try {
        const button = document.querySelector(`tr[data-job-id="${jobId}"] .resume-button`);
        button.disabled = true;
        button.textContent = 'Tailoring...';
        
        const response = await fetch(`/jobs/${jobId}/tailor-resume`, {
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