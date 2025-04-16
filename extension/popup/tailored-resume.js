document.addEventListener('DOMContentLoaded', () => {
    // Get job ID from URL parameters
    const urlParams = new URLSearchParams(window.location.search);
    const jobId = urlParams.get('jobId');
    
    if (!jobId) {
        showError('No job ID provided');
        return;
    }
    
    loadJobAndResume(jobId);
});

async function loadJobAndResume(jobId) {
    try {
        // Load job details
        const jobResponse = await fetch(`/jobs/${jobId}`);
        if (!jobResponse.ok) {
            throw new Error(`HTTP error! status: ${jobResponse.status}`);
        }
        const job = await jobResponse.json();
        
        // Load tailored resume
        const resumeResponse = await fetch(`/jobs/${jobId}/tailored-resume`);
        if (!resumeResponse.ok) {
            throw new Error(`HTTP error! status: ${resumeResponse.status}`);
        }
        const resume = await resumeResponse.json();
        
        // Update the UI
        document.getElementById('jobDescription').textContent = job.description || 'No description available';
        document.getElementById('tailoredResume').textContent = resume.content || 'No tailored resume available';
        
    } catch (error) {
        console.error('Error loading job and resume:', error);
        showError('Error loading job and resume details');
    }
}

function showError(message) {
    const container = document.querySelector('.split-container');
    container.innerHTML = `
        <div style="padding: 20px; color: red;">
            Error: ${message}
        </div>
    `;
} 