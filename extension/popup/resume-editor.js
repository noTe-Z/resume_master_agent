document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements - Editor
    const inputName = document.getElementById('input-name');
    const inputEmail = document.getElementById('input-email');
    const inputPhone = document.getElementById('input-phone');
    const inputLinkedin = document.getElementById('input-linkedin');
    const inputSummary = document.getElementById('input-summary');
    const educationItems = document.getElementById('education-items');
    const experienceItems = document.getElementById('experience-items');
    const addEducationBtn = document.getElementById('add-education');
    const addExperienceBtn = document.getElementById('add-experience');
    
    // DOM Elements - Preview
    const previewName = document.getElementById('preview-name');
    const previewContact = document.getElementById('preview-contact');
    const previewSummary = document.getElementById('preview-summary');
    const previewEducation = document.getElementById('preview-education');
    const previewExperience = document.getElementById('preview-experience');
    
    // DOM Elements - Navigation
    const backButton = document.getElementById('backToAnalysis');
    const editBaseResumeButton = document.getElementById('editBaseResume');
    
    // Data storage for resume sections
    let educationEntries = [];
    let experienceEntries = [];
    
    // Initialize with sample data
    initializeWithSampleData();
    
    // Event listeners for real-time updates
    inputName.addEventListener('input', updateName);
    inputEmail.addEventListener('input', updateContactInfo);
    inputPhone.addEventListener('input', updateContactInfo);
    inputLinkedin.addEventListener('input', updateContactInfo);
    inputSummary.addEventListener('input', updateSummary);
    
    // Add buttons event listeners
    addEducationBtn.addEventListener('click', addEducationEntry);
    addExperienceBtn.addEventListener('click', addExperienceEntry);
    
    // Navigation button event listeners
    backButton.addEventListener('click', navigateToAnalysis);
    editBaseResumeButton.addEventListener('click', navigateToBaseResume);
    
    // Real-time update functions
    function updateName() {
        previewName.textContent = inputName.value || 'Your Name';
    }
    
    function updateContactInfo() {
        let contactText = '';
        if (inputEmail.value) contactText += `Email: ${inputEmail.value}`;
        if (inputPhone.value) contactText += (contactText ? ' | ' : '') + `Phone: ${inputPhone.value}`;
        if (inputLinkedin.value) contactText += (contactText ? ' | ' : '') + `LinkedIn: ${inputLinkedin.value}`;
        
        previewContact.textContent = contactText || 'Email: your.email@example.com | Phone: (123) 456-7890 | LinkedIn: linkedin.com/in/yourname';
    }
    
    function updateSummary() {
        previewSummary.textContent = inputSummary.value || 'Your professional summary will appear here...';
    }
    
    // Education entry functions
    function createEducationEntryHTML(id, isNew = false) {
        const entry = isNew ? {
            school: '',
            degree: '',
            dates: '',
            gpa: ''
        } : educationEntries[id];
        
        const educationHTML = document.createElement('div');
        educationHTML.className = 'education-item';
        educationHTML.dataset.id = id;
        educationHTML.innerHTML = `
            <button class="delete-item" data-id="${id}">×</button>
            <div class="form-group">
                <label class="form-label" for="edu-school-${id}">Institution</label>
                <input type="text" id="edu-school-${id}" class="form-control edu-school" placeholder="University or School Name" value="${entry.school}">
            </div>
            <div class="form-group">
                <label class="form-label" for="edu-degree-${id}">Degree</label>
                <input type="text" id="edu-degree-${id}" class="form-control edu-degree" placeholder="Bachelor of Science, Computer Science" value="${entry.degree}">
            </div>
            <div class="form-group">
                <label class="form-label" for="edu-dates-${id}">Dates</label>
                <input type="text" id="edu-dates-${id}" class="form-control edu-dates" placeholder="Aug 2018 - May 2022" value="${entry.dates}">
            </div>
            <div class="form-group">
                <label class="form-label" for="edu-gpa-${id}">GPA (Optional)</label>
                <input type="text" id="edu-gpa-${id}" class="form-control edu-gpa" placeholder="3.8/4.0" value="${entry.gpa}">
            </div>
        `;
        
        // Add event listeners to form fields
        const inputs = educationHTML.querySelectorAll('input');
        inputs.forEach(input => {
            input.addEventListener('input', () => updateEducationPreview());
        });
        
        // Add event listener to delete button
        const deleteBtn = educationHTML.querySelector('.delete-item');
        deleteBtn.addEventListener('click', () => {
            deleteEducationEntry(id);
        });
        
        return educationHTML;
    }
    
    function addEducationEntry() {
        const id = educationEntries.length;
        educationEntries.push({
            school: '',
            degree: '',
            dates: '',
            gpa: ''
        });
        
        educationItems.appendChild(createEducationEntryHTML(id, true));
        updateEducationPreview();
    }
    
    function deleteEducationEntry(id) {
        // Remove from DOM
        const entryElement = document.querySelector(`.education-item[data-id="${id}"]`);
        if (entryElement) {
            entryElement.remove();
        }
        
        // Remove from data array (or mark as deleted)
        educationEntries[id] = null;
        
        // Update preview
        updateEducationPreview();
    }
    
    function updateEducationPreview() {
        // Clear existing preview
        previewEducation.innerHTML = '';
        
        // Generate preview for each non-deleted education entry
        educationEntries.forEach((entry, index) => {
            if (!entry) return; // Skip deleted entries
            
            // Get current values from form
            const schoolInput = document.getElementById(`edu-school-${index}`);
            const degreeInput = document.getElementById(`edu-degree-${index}`);
            const datesInput = document.getElementById(`edu-dates-${index}`);
            const gpaInput = document.getElementById(`edu-gpa-${index}`);
            
            if (!schoolInput) return; // Skip if element not found
            
            // Update data object
            entry.school = schoolInput.value;
            entry.degree = degreeInput.value;
            entry.dates = datesInput.value;
            entry.gpa = gpaInput.value;
            
            // Create preview element
            const previewEntry = document.createElement('div');
            previewEntry.className = 'education-entry';
            
            const entryHeader = document.createElement('div');
            entryHeader.className = 'entry-header';
            
            const schoolSpan = document.createElement('span');
            schoolSpan.className = 'entry-school';
            schoolSpan.textContent = entry.school || 'University Name';
            
            const datesSpan = document.createElement('span');
            datesSpan.className = 'entry-dates';
            datesSpan.textContent = entry.dates || 'Dates';
            
            entryHeader.appendChild(schoolSpan);
            entryHeader.appendChild(datesSpan);
            previewEntry.appendChild(entryHeader);
            
            const degreeDiv = document.createElement('div');
            degreeDiv.className = 'entry-degree';
            let degreeText = entry.degree || 'Degree';
            if (entry.gpa) {
                degreeText += ` (GPA: ${entry.gpa})`;
            }
            degreeDiv.textContent = degreeText;
            previewEntry.appendChild(degreeDiv);
            
            previewEducation.appendChild(previewEntry);
        });
        
        // If no entries, show placeholder
        if (previewEducation.children.length === 0) {
            previewEducation.innerHTML = '<div class="education-entry"><div class="entry-header"><span class="entry-school">University Name</span><span class="entry-dates">Dates</span></div><div class="entry-degree">Degree</div></div>';
        }
    }
    
    // Experience entry functions
    function createExperienceEntryHTML(id, isNew = false) {
        const entry = isNew ? {
            company: '',
            title: '',
            dates: '',
            description: ''
        } : experienceEntries[id];
        
        const experienceHTML = document.createElement('div');
        experienceHTML.className = 'experience-item';
        experienceHTML.dataset.id = id;
        experienceHTML.innerHTML = `
            <button class="delete-item" data-id="${id}">×</button>
            <div class="form-group">
                <label class="form-label" for="exp-company-${id}">Company</label>
                <input type="text" id="exp-company-${id}" class="form-control exp-company" placeholder="Company Name" value="${entry.company}">
            </div>
            <div class="form-group">
                <label class="form-label" for="exp-title-${id}">Job Title</label>
                <input type="text" id="exp-title-${id}" class="form-control exp-title" placeholder="Software Engineer" value="${entry.title}">
            </div>
            <div class="form-group">
                <label class="form-label" for="exp-dates-${id}">Dates</label>
                <input type="text" id="exp-dates-${id}" class="form-control exp-dates" placeholder="Jan 2020 - Present" value="${entry.dates}">
            </div>
            <div class="form-group">
                <label class="form-label" for="exp-description-${id}">Description</label>
                <textarea id="exp-description-${id}" class="form-control exp-description" placeholder="Describe your role, responsibilities, and achievements...">${entry.description}</textarea>
            </div>
        `;
        
        // Add event listeners to form fields
        const inputs = experienceHTML.querySelectorAll('input, textarea');
        inputs.forEach(input => {
            input.addEventListener('input', () => updateExperiencePreview());
        });
        
        // Add event listener to delete button
        const deleteBtn = experienceHTML.querySelector('.delete-item');
        deleteBtn.addEventListener('click', () => {
            deleteExperienceEntry(id);
        });
        
        return experienceHTML;
    }
    
    function addExperienceEntry() {
        const id = experienceEntries.length;
        experienceEntries.push({
            company: '',
            title: '',
            dates: '',
            description: ''
        });
        
        experienceItems.appendChild(createExperienceEntryHTML(id, true));
        updateExperiencePreview();
    }
    
    function deleteExperienceEntry(id) {
        // Remove from DOM
        const entryElement = document.querySelector(`.experience-item[data-id="${id}"]`);
        if (entryElement) {
            entryElement.remove();
        }
        
        // Remove from data array (or mark as deleted)
        experienceEntries[id] = null;
        
        // Update preview
        updateExperiencePreview();
    }
    
    function updateExperiencePreview() {
        // Clear existing preview
        previewExperience.innerHTML = '';
        
        // Generate preview for each non-deleted experience entry
        experienceEntries.forEach((entry, index) => {
            if (!entry) return; // Skip deleted entries
            
            // Get current values from form
            const companyInput = document.getElementById(`exp-company-${index}`);
            const titleInput = document.getElementById(`exp-title-${index}`);
            const datesInput = document.getElementById(`exp-dates-${index}`);
            const descriptionInput = document.getElementById(`exp-description-${index}`);
            
            if (!companyInput) return; // Skip if element not found
            
            // Update data object
            entry.company = companyInput.value;
            entry.title = titleInput.value;
            entry.dates = datesInput.value;
            entry.description = descriptionInput.value;
            
            // Create preview element
            const previewEntry = document.createElement('div');
            previewEntry.className = 'experience-entry';
            
            const entryHeader = document.createElement('div');
            entryHeader.className = 'entry-header';
            
            const companySpan = document.createElement('span');
            companySpan.className = 'entry-company';
            companySpan.textContent = entry.company || 'Company Name';
            
            const datesSpan = document.createElement('span');
            datesSpan.className = 'entry-dates';
            datesSpan.textContent = entry.dates || 'Dates';
            
            entryHeader.appendChild(companySpan);
            entryHeader.appendChild(datesSpan);
            previewEntry.appendChild(entryHeader);
            
            const titleDiv = document.createElement('div');
            titleDiv.className = 'entry-position';
            titleDiv.textContent = entry.title || 'Job Title';
            previewEntry.appendChild(titleDiv);
            
            const descriptionDiv = document.createElement('div');
            descriptionDiv.className = 'entry-description';
            descriptionDiv.textContent = entry.description || 'Job description goes here...';
            previewEntry.appendChild(descriptionDiv);
            
            previewExperience.appendChild(previewEntry);
        });
        
        // If no entries, show placeholder
        if (previewExperience.children.length === 0) {
            previewExperience.innerHTML = '<div class="experience-entry"><div class="entry-header"><span class="entry-company">Company Name</span><span class="entry-dates">Dates</span></div><div class="entry-position">Job Title</div><div class="entry-description">Job description goes here...</div></div>';
        }
    }
    
    // Navigation functions
    function navigateToAnalysis() {
        window.location.href = '/';
    }
    
    function navigateToBaseResume() {
        // You can implement this function to navigate to the base resume editor
        alert('Base Resume Editor is not implemented yet.');
    }
    
    // Initialize with sample data
    function initializeWithSampleData() {
        // Fetch resume data from server or use sample data
        fetchResumeData()
            .then(data => {
                if (data) {
                    populateFormFields(data);
                } else {
                    // Use sample data if no data was returned
                    useSampleData();
                }
                
                // Update all previews
                updateName();
                updateContactInfo();
                updateSummary();
                updateEducationPreview();
                updateExperiencePreview();
            })
            .catch(error => {
                console.error('Error loading resume data:', error);
                useSampleData();
            });
    }
    
    function fetchResumeData() {
        // This function should fetch the resume data from the server
        // For now, we'll return a Promise that resolves to null to use sample data
        return Promise.resolve(null);
    }
    
    function populateFormFields(data) {
        // Populate personal info
        inputName.value = data.name || '';
        inputEmail.value = data.email || '';
        inputPhone.value = data.phone || '';
        inputLinkedin.value = data.linkedin || '';
        inputSummary.value = data.summary || '';
        
        // Populate education entries
        educationEntries = data.education || [];
        educationItems.innerHTML = '';
        educationEntries.forEach((entry, index) => {
            educationItems.appendChild(createEducationEntryHTML(index));
        });
        
        // Populate experience entries
        experienceEntries = data.experience || [];
        experienceItems.innerHTML = '';
        experienceEntries.forEach((entry, index) => {
            experienceItems.appendChild(createExperienceEntryHTML(index));
        });
    }
    
    function useSampleData() {
        // Sample data to use if no data is available
        inputName.value = 'John Doe';
        inputEmail.value = 'john.doe@example.com';
        inputPhone.value = '(555) 123-4567';
        inputLinkedin.value = 'linkedin.com/in/johndoe';
        inputSummary.value = 'Experienced software engineer with a passion for building user-friendly web applications. Skilled in JavaScript, React, and Node.js.';
        
        // Add sample education entries
        educationEntries = [
            {
                school: 'University of Example',
                degree: 'Bachelor of Science, Computer Science',
                dates: 'Aug 2015 - May 2019',
                gpa: '3.8/4.0'
            }
        ];
        
        educationItems.innerHTML = '';
        educationEntries.forEach((entry, index) => {
            educationItems.appendChild(createEducationEntryHTML(index));
        });
        
        // Add sample experience entries
        experienceEntries = [
            {
                company: 'Tech Company Inc.',
                title: 'Senior Software Engineer',
                dates: 'Jun 2020 - Present',
                description: 'Developed and maintained web applications using React and Node.js. Led a team of 5 engineers in delivering critical projects on time.'
            },
            {
                company: 'Startup Ltd.',
                title: 'Software Developer',
                dates: 'Jul 2019 - May 2020',
                description: 'Built and shipped features for a SaaS platform serving over 10,000 customers. Improved site performance by 30%.'
            }
        ];
        
        experienceItems.innerHTML = '';
        experienceEntries.forEach((entry, index) => {
            experienceItems.appendChild(createExperienceEntryHTML(index));
        });
    }
}); 