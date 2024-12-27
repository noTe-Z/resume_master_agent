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
        // Try to find the apply button with various selectors
        const applyButtonSelectors = [
            '.jobs-apply-button',
            '.jobs-unified-top-card__apply-button',
            '[data-control-name="jobdetails_topcard_inapply"]',
            '.jobs-apply-button--top-card',
            '.jobs-s-apply button',
            '.jobs-apply-button__text'
        ];

        let applyButton = null;
        for (const selector of applyButtonSelectors) {
            applyButton = document.querySelector(selector);
            if (applyButton) break;
        }

        if (!applyButton) {
            console.log('Apply button not found, trying alternative methods');
            // Try to get the URL from the job title link
            const titleLink = document.querySelector('.job-details-jobs-unified-top-card__job-title h1 a');
            if (titleLink) {
                const href = titleLink.getAttribute('href');
                if (href) {
                    const absoluteUrl = href.startsWith('http') ? href : new URL(href, window.location.origin).href;
                    console.log('Found apply URL from title link:', absoluteUrl);
                    resolve(absoluteUrl);
                    return;
                }
            }
            
            // If all else fails, use the current page URL
            console.log('No apply URL found, using current page URL');
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
            console.log('Found apply URL from button:', applyUrl);
            // If the URL is relative, make it absolute
            const absoluteUrl = applyUrl.startsWith('http') ? applyUrl : new URL(applyUrl, window.location.origin).href;
            resolve(absoluteUrl);
        } else {
            // If we can't find the URL in the button, try to get it from the parent element
            const parentElement = applyButton.closest('a, button');
            if (parentElement) {
                const parentUrl = parentElement.getAttribute('href') ||
                                parentElement.getAttribute('data-apply-url') ||
                                parentElement.getAttribute('data-job-url');
                if (parentUrl) {
                    console.log('Found apply URL from parent element:', parentUrl);
                    const absoluteUrl = parentUrl.startsWith('http') ? parentUrl : new URL(parentUrl, window.location.origin).href;
                    resolve(absoluteUrl);
                    return;
                }
            }
            
            // If we still can't find the URL, use the current page URL
            console.log('No apply URL found in button, using current page URL');
            resolve(window.location.href);
        }
    });
}

function createSaveButton() {
    // Create button
    const button = document.createElement('button');
    button.textContent = 'Save Job';
    button.style.cssText = `
        background-color: #0a66c2;
        color: white;
        border: none;
        border-radius: 16px;
        padding: 6px 16px;
        font-size: 14px;
        font-weight: 600;
        cursor: pointer;
        margin-left: 12px;
    `;
    
    // Add hover effect
    button.addEventListener('mouseenter', () => {
        button.style.backgroundColor = '#004182';
    });
    button.addEventListener('mouseleave', () => {
        button.style.backgroundColor = '#0a66c2';
    });
    
    // Add click handler
    button.addEventListener('click', async () => {
        try {
            // Get job details
            const titleElement = document.querySelector('.job-details-jobs-unified-top-card__job-title h1');
            const companyElement = document.querySelector('.job-details-jobs-unified-top-card__company-name');
            const descriptionElement = document.querySelector('.jobs-description-content__text');
            
            if (!titleElement || !companyElement) {
                console.error('Could not find required job elements');
                return;
            }

            // Get application URL using the existing function
            const applyLink = await getApplicationUrl();
            console.log('Application URL:', applyLink);
            
            const jobData = {
                title: titleElement.textContent.trim(),
                company: companyElement.textContent.trim(),
                description: descriptionElement ? descriptionElement.textContent.trim() : '',
                apply_link: applyLink
            };

            console.log('Sending job data:', jobData);
            
            // Save job
            const response = await fetch('http://localhost:3000/save-job', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(jobData)
            });
            
            if (!response.ok) {
                throw new Error('Failed to save job');
            }
            
            // Update button to show success
            button.textContent = 'Saved!';
            button.style.backgroundColor = '#057642';
            setTimeout(() => {
                button.textContent = 'Save Job';
                button.style.backgroundColor = '#0a66c2';
            }, 2000);
            
        } catch (error) {
            console.error('Error saving job:', error);
            button.textContent = 'Error!';
            button.style.backgroundColor = '#cc1016';
            setTimeout(() => {
                button.textContent = 'Save Job';
                button.style.backgroundColor = '#0a66c2';
            }, 2000);
        }
    });
    
    return button;
}

function insertSaveButton() {
    // Find the job title container
    const titleContainer = document.querySelector('.job-details-jobs-unified-top-card__job-title');
    if (!titleContainer) {
        console.error('Could not find job title container');
        return;
    }
    
    // Check if button already exists
    if (titleContainer.querySelector('button[data-purpose="save-job"]')) {
        return;
    }
    
    // Create and insert button
    const saveButton = createSaveButton();
    saveButton.setAttribute('data-purpose', 'save-job');
    titleContainer.appendChild(saveButton);
}

// Initial insertion
setTimeout(insertSaveButton, 1000);

// Watch for URL changes (LinkedIn uses client-side routing)
let lastUrl = location.href;
new MutationObserver(() => {
    const url = location.href;
    if (url !== lastUrl) {
        lastUrl = url;
        setTimeout(insertSaveButton, 1000);
    }
}).observe(document, { subtree: true, childList: true }); 