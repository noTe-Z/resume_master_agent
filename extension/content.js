function waitForElement(selector, maxAttempts = 10, interval = 1000) {
    return new Promise((resolve, reject) => {
        let attempts = 0;
        
        const checkElement = () => {
            const element = document.querySelector(selector);
            if (element) {
                resolve(element);
                return;
            }
            
            attempts++;
            if (attempts >= maxAttempts) {
                reject(new Error(`Element ${selector} not found after ${maxAttempts} attempts`));
                return;
            }
            
            setTimeout(checkElement, interval);
        };
        
        checkElement();
    });
}

function getApplicationUrl() {
    return new Promise((resolve) => {
        // Try to find the apply button
        const applyButton = document.querySelector('.jobs-apply-button, .jobs-unified-top-card__apply-button, [data-control-name="jobdetails_topcard_inapply"]');
        if (!applyButton) {
            console.log('Apply button not found');
            resolve(window.location.href);
            return;
        }

        // Try to get the URL from various attributes
        const applyUrl = applyButton.getAttribute('href') || 
                        applyButton.getAttribute('data-apply-url') || 
                        applyButton.getAttribute('data-job-url') ||
                        applyButton.dataset.applyUrl ||
                        applyButton.dataset.jobUrl;

        if (applyUrl) {
            console.log('Found apply URL:', applyUrl);
            // If the URL is relative, make it absolute
            const absoluteUrl = applyUrl.startsWith('http') ? applyUrl : new URL(applyUrl, window.location.origin).href;
            resolve(absoluteUrl);
        } else {
            // If we can't find the URL, use the current page URL
            console.log('No apply URL found, using current page URL');
            resolve(window.location.href);
        }
    });
}

function createSaveButton() {
    // Remove any existing save buttons
    const existingSaveButtons = document.querySelectorAll('.linkedin-job-saver-btn');
    existingSaveButtons.forEach(btn => btn.remove());

    // Create new save button
    const saveButton = document.createElement('button');
    saveButton.textContent = 'Save Job';
    saveButton.className = 'linkedin-job-saver-btn artdeco-button artdeco-button--2 artdeco-button--primary';
    saveButton.style.marginRight = '8px';

    // Add click event listener
    saveButton.addEventListener('click', async () => {
        try {
            // Get job title
            const titleElement = document.querySelector('h1.job-details-jobs-unified-top-card__job-title, h1.t-24, .jobs-unified-top-card__job-title');
            if (!titleElement) {
                throw new Error('Could not find job title');
            }
            const title = titleElement.textContent.trim();

            // Get company name
            const companyElement = document.querySelector('.job-details-jobs-unified-top-card__company-name a, .jobs-unified-top-card__company-name a, .jobs-unified-top-card__company-name');
            const company = companyElement ? companyElement.textContent.trim() : '';

            // Get job description
            const descriptionElement = document.querySelector('.jobs-description__content, .jobs-description, .jobs-unified-top-card__description');
            const description = descriptionElement ? descriptionElement.textContent.trim() : '';

            // Get current URL
            const url = window.location.href;

            // Get application URL
            const applyLink = await getApplicationUrl();

            console.log('Extracted job details:', {
                title,
                company,
                description: description.substring(0, 100) + '...',
                applyLink
            });

            // Prepare job data
            const jobData = {
                title: title,
                company: company,
                url: url,
                description: description,
                applyLink: applyLink
            };

            // Send data to backend
            const response = await fetch('http://localhost:3000/save-job', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify(jobData)
            });

            const result = await response.json();
            console.log('Server response:', result);

            // Update button to show success/error
            if (response.ok) {
                saveButton.textContent = 'Saved!';
                saveButton.style.backgroundColor = '#057642';
            setTimeout(() => {
                    saveButton.textContent = 'Save Job';
                saveButton.style.backgroundColor = '';
            }, 2000);
            } else {
                throw new Error(result.error || 'Failed to save job');
            }
        } catch (error) {
            console.error('Error saving job:', error);
            saveButton.textContent = 'Error!';
            saveButton.style.backgroundColor = '#d11124';
            setTimeout(() => {
                saveButton.textContent = 'Save Job';
                saveButton.style.backgroundColor = '';
            }, 2000);
        }
    });

    return saveButton;
}

async function insertSaveButton() {
    try {
        // Try different selectors for the button container
        const containerSelectors = [
            '.jobs-unified-top-card__actions',
            '.jobs-s-apply',
            '.jobs-unified-top-card__button-container',
            '.jobs-unified-top-card__actions-container',
            '.jobs-details-top-card__actions-container'
        ];

        let container = null;
        for (const selector of containerSelectors) {
            container = await waitForElement(selector).catch(() => null);
            if (container) break;
        }

        if (!container) {
            console.error('Could not find button container');
            return;
        }

        const saveButton = createSaveButton();
        container.insertBefore(saveButton, container.firstChild);
        console.log('Save button inserted successfully');
    } catch (error) {
        console.error('Error inserting save button:', error);
    }
}

// Initial button creation with retry
insertSaveButton();

// Create an observer to watch for changes in the job details section
const observer = new MutationObserver((mutations) => {
    // Check if our button exists
    if (!document.querySelector('.linkedin-job-saver-btn')) {
        insertSaveButton();
    }
});

// Start observing the main content area for SPA navigation
const mainContent = document.querySelector('#main-content, #main, .jobs-search__job-details');
if (mainContent) {
    observer.observe(mainContent, { 
        childList: true,
        subtree: true,
        attributes: true,
        characterData: true
    });
    console.log('Started observing main content');
} else {
    console.log('Main content not found, will retry observation');
    setTimeout(() => {
        const retryContent = document.querySelector('#main-content, #main, .jobs-search__job-details');
        if (retryContent) {
            observer.observe(retryContent, { 
                childList: true, 
                subtree: true,
                attributes: true,
                characterData: true
            });
            console.log('Started observing main content after retry');
        }
    }, 2000);
} 