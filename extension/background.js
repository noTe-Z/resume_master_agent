// Keep track of tabs opened for job applications
const applicationTabs = new Map();

// List of known application domains
const APPLICATION_DOMAINS = [
    'egup.fa.us2.oraclecloud.com',
    'oracle.com',
    'greenhouse.io',
    'lever.co',
    'workday.com',
    'myworkdayjobs.com',
    'brassring.com',
    'smartrecruiters.com',
    'icims.com',
    'jobvite.com'
];

// Listen for messages from content script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'openTab') {
        console.log('Opening application URL:', request.url);
        
        // Create a new tab for the application
        chrome.tabs.create({ url: request.url, active: false }, (tab) => {
            // Store the tab ID and callback
            applicationTabs.set(tab.id, sendResponse);
            
            // Set up a listener for this specific tab
            const tabUpdateListener = (tabId, changeInfo) => {
                if (tabId === tab.id && changeInfo.url) {
                    console.log('Tab URL changed:', changeInfo.url);
                    
                    // Check if the URL contains any known application domains
                    if (APPLICATION_DOMAINS.some(domain => changeInfo.url.includes(domain))) {
                        console.log('Found application URL:', changeInfo.url);
                        
                        // Get the callback for this tab
                        const callback = applicationTabs.get(tab.id);
                        if (callback) {
                            // Send the URL back to the content script
                            callback({ url: changeInfo.url });
                            applicationTabs.delete(tab.id);
                            
                            // Close the tab after a short delay
                            setTimeout(() => {
                                chrome.tabs.remove(tab.id);
                            }, 500);
                            
                            // Remove the listener
                            chrome.tabs.onUpdated.removeListener(tabUpdateListener);
                        }
                    }
                }
            };
            
            // Add the listener
            chrome.tabs.onUpdated.addListener(tabUpdateListener);
            
            // Set a timeout to clean up if we don't get a URL within 5 seconds
            setTimeout(() => {
                if (applicationTabs.has(tab.id)) {
                    console.log('Timeout reached, using original URL');
                    const callback = applicationTabs.get(tab.id);
                    if (callback) {
                        callback({ url: request.url });
                    }
                    applicationTabs.delete(tab.id);
                    chrome.tabs.remove(tab.id);
                }
            }, 5000);
        });
        
        // Return true to indicate we'll send a response asynchronously
        return true;
    }
});