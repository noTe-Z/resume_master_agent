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
            // Get job details with multiple selectors for each element
            let titleElement = null;
            const titleSelectors = [
                '.job-details-jobs-unified-top-card__job-title h1',
                '.jobs-unified-top-card__job-title h1',
                '.jobs-unified-top-card__title h1',
                '.jobs-search__job-details--title h1',
                '.jobs-details-top-card__title-container h1',
                '.jobs-unified-top-card h1',
                'h1.job-title'
            ];
            
            for (const selector of titleSelectors) {
                titleElement = document.querySelector(selector);
                if (titleElement) break;
            }
            
            // Fallback: try to find any h1 element within the job details section
            if (!titleElement) {
                const jobDetailsSection = document.querySelector('.jobs-unified-top-card, .job-view-layout, .jobs-details, .job-details-jobs-unified-top-card');
                if (jobDetailsSection) {
                    titleElement = jobDetailsSection.querySelector('h1');
                }
            }
            
            let companyElement = null;
            const companySelectors = [
                '.job-details-jobs-unified-top-card__company-name',
                '.jobs-unified-top-card__company-name',
                '.jobs-unified-top-card__subtitle-primary',
                '.jobs-top-card__company-url',
                '.jobs-details-top-card__company-info',
                '[data-test-job-card-company-name]'
            ];
            
            for (const selector of companySelectors) {
                companyElement = document.querySelector(selector);
                if (companyElement) break;
            }
            
            let descriptionElement = null;
            const descriptionSelectors = [
                '.jobs-description__content',
                '.jobs-description',
                '.jobs-unified-top-card__description',
                '.jobs-box__html-content',
                '.jobs-details'
            ];
            
            for (const selector of descriptionSelectors) {
                descriptionElement = document.querySelector(selector);
                if (descriptionElement) break;
            }
            
            if (!titleElement || !companyElement) {
                console.error('Could not find required job elements', { 
                    titleFound: !!titleElement,
                    companyFound: !!companyElement
                });
                alert('Could not find job details. Please try again on a LinkedIn job page.');
                return;
            }

            // Get application URL using the existing function
            const applyLink = await getApplicationUrl();
            console.log('Application URL:', applyLink);
            
            // Clean the description by removing "About the job" prefix and cleaning up the text
            let description = descriptionElement ? descriptionElement.textContent.trim() : '';
            
            // Remove "About the job" prefix with case insensitivity
            description = description.replace(/^About the job\s*:?\s*/i, '');
            
            // Remove excessive whitespace and normalize line breaks
            description = description.replace(/\s+/g, ' ');
            
            // Clean up common LinkedIn job description artifacts
            description = description.replace(/Show more/g, '');
            description = description.replace(/Show less/g, '');
            
            const jobData = {
                title: titleElement.textContent.trim(),
                company: companyElement.textContent.trim(),
                description: description,
                apply_link: applyLink
            };

            console.log('Sending job data:', jobData);
            
            // Save job
            const response = await fetch('/save-job', {
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
    // Find the job title container with multiple possible selectors
    const titleContainerSelectors = [
        '.job-details-jobs-unified-top-card__job-title',
        '.jobs-unified-top-card__job-title',
        '.jobs-unified-top-card__title',
        '.jobs-search__job-details--title',
        '.jobs-details-top-card__title-container'
    ];
    
    let titleContainer = null;
    for (const selector of titleContainerSelectors) {
        titleContainer = document.querySelector(selector);
        if (titleContainer) {
            console.log(`Found title container with selector: ${selector}`);
            break;
        }
    }
    
    if (!titleContainer) {
        // Try to find any container that contains the job title
        const h1Elements = document.querySelectorAll('h1');
        for (const h1 of h1Elements) {
            // Check if this h1 is likely to be a job title (within a job details section)
            const isInJobDetails = h1.closest('.jobs-unified-top-card, .job-view-layout, .jobs-details, .job-details-jobs-unified-top-card');
            if (isInJobDetails) {
                titleContainer = h1.parentElement;
                console.log('Found title container via h1 element in job details');
                break;
            }
        }
    }
    
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

// Initialize the extension
function initializeExtension() {
    console.log('Resume Agent: Initializing on LinkedIn page', window.location.href);
    
    // Check if we're on a feed page that might show job postings
    const isFeedPage = window.location.href.includes('linkedin.com/feed/');
    
    // Check if we're on a dedicated job page
    const isJobPage = window.location.href.includes('linkedin.com/jobs/') || 
                      window.location.href.includes('linkedin.com/job/') ||
                      window.location.href.includes('/view/');
    
    if (!isJobPage && !isFeedPage) {
        console.log('Resume Agent: Not a job or feed page, skipping initialization');
        return;
    }
    
    if (isFeedPage) {
        console.log('Resume Agent: On feed page, looking for job posts');
        // For feed pages, we need a different approach to find job posts
        // Try to find job cards or job posts within the feed
        setTimeout(() => {
            const feedJobPosts = document.querySelectorAll('.feed-shared-update-v2__content');
            if (feedJobPosts.length > 0) {
                console.log(`Resume Agent: Found ${feedJobPosts.length} potential job posts in feed`);
                // Process each post to see if it's a job post
                feedJobPosts.forEach(post => {
                    const jobTitleElement = post.querySelector('h3, .feed-shared-update-v2__description');
                    if (jobTitleElement && jobTitleElement.textContent.includes('is hiring')) {
                        console.log('Resume Agent: Found a job post in feed', jobTitleElement.textContent);
                        // Add save button to this post
                        if (!post.querySelector('button[data-purpose="save-job"]')) {
                            const saveButton = createSaveButton();
                            saveButton.setAttribute('data-purpose', 'save-job');
                            
                            // Find a good place to insert the button
                            const actionBar = post.querySelector('.feed-shared-social-actions');
                            if (actionBar) {
                                actionBar.appendChild(saveButton);
                                console.log('Resume Agent: Added save button to job post in feed');
                            }
                        }
                    }
                });
            }
        }, 2000); // Wait for feed to load
    }
    
    if (isJobPage) {
        console.log('Resume Agent: Detected job page, inserting save button');
        
        // Try a few times as the page might be loading dynamically
        const maxAttempts = 5;
        let attempts = 0;
        
        const tryInsertButton = () => {
            attempts++;
            console.log(`Resume Agent: Attempt ${attempts} to insert save button`);
            insertSaveButton();
            
            if (attempts < maxAttempts) {
                setTimeout(tryInsertButton, 1500);
            }
        };
        
        tryInsertButton();
    }
}

// Initial insertion
window.addEventListener('load', initializeExtension);

// Watch for URL changes (LinkedIn uses client-side routing)
let lastUrl = location.href;
const observer = new MutationObserver(() => {
    const url = location.href;
    if (url !== lastUrl) {
        lastUrl = url;
        console.log('Resume Agent: URL changed to', url);
        setTimeout(initializeExtension, 1000);
    }
});

// Start observing
observer.observe(document, { subtree: true, childList: true });

console.log('Resume Agent: Content script loaded');