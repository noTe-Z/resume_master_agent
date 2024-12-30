import os
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import sqlite3
from datetime import datetime

@pytest.fixture(scope="function")
def test_db():
    # Create a test database
    db_path = 'jobs.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables
    cursor.executescript('''
        DROP TABLE IF EXISTS jobs;
        DROP TABLE IF EXISTS tailored_resumes;
        
        CREATE TABLE jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            description TEXT,
            apply_link TEXT,
            status TEXT DEFAULT 'to_apply',
            saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            applied_at TIMESTAMP
        );
        
        CREATE TABLE tailored_resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
        );
    ''')
    
    # Insert test data
    cursor.execute('''
        INSERT INTO jobs (title, company, description, apply_link, status)
        VALUES (?, ?, ?, ?, ?)
    ''', ('Software Engineer', 'Test Company', 'Test job description', 'http://example.com/apply', 'to_apply'))
    
    conn.commit()
    conn.close()
    
    yield db_path
    
    # Cleanup
    if os.path.exists(db_path):
        os.remove(db_path)

@pytest.fixture(scope="function")
def driver():
    # Set up Chrome options
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--disable-gpu')  # Required for headless mode
    options.add_argument('--no-sandbox')  # Required for running as root
    options.add_argument('--disable-dev-shm-usage')  # Required for CI environments
    options.add_argument('--window-size=1920,1080')  # Set window size
    options.add_argument('--remote-debugging-port=9222')  # Enable debugging
    options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})  # Enable console logging
    
    # Create driver
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)  # Set implicit wait
    
    yield driver
    
    # Print any remaining logs before quitting
    logs = driver.get_log('browser')
    if logs:
        print("\nFinal browser logs:")
        for log in logs:
            print(log)
    
    # Cleanup
    driver.quit()

def test_tailor_resume_button_exists(driver, test_db):
    # Navigate to jobs page
    driver.get('http://localhost:8000/jobs.html')
    
    try:
        # Wait for table to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "jobsTableBody"))
        )
        
        # Wait for jobs to be loaded (table should have at least one row)
        WebDriverWait(driver, 10).until(
            lambda d: len(d.find_elements(By.TAG_NAME, "tr")) > 0 and 
                     d.find_element(By.ID, "jobsTableBody").text.strip() != ''
        )
        
        # Print table contents for debugging
        table = driver.find_element(By.ID, "jobsTableBody")
        print(f"Table HTML: {table.get_attribute('innerHTML')}")
        
        # Get page source for debugging
        print(f"Page source: {driver.page_source}")
        
        # Print console logs
        logs = driver.get_log('browser')
        print("Browser logs:")
        for log in logs:
            print(log)
        
        # Check if Tailor Resume button exists
        buttons = driver.find_elements(By.CLASS_NAME, "resume-button")
        assert len(buttons) > 0, "No resume buttons found"
        button = buttons[0]
        
        # Verify button properties
        assert button.is_displayed(), "Resume button is not visible"
        assert button.is_enabled(), "Resume button is not enabled"
        assert "Tailor Resume" in button.text, f"Unexpected button text: {button.text}"
        
    except Exception as e:
        print(f"Error in test: {str(e)}")
        # Print current page source
        print(f"Page source at error: {driver.page_source}")
        raise e

def test_tailor_resume_workflow(driver, test_db):
    # Navigate to jobs page
    driver.get('http://localhost:8000/jobs.html')
    
    try:
        # Wait for table to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "jobsTableBody"))
        )
        
        # Wait for jobs to be loaded
        WebDriverWait(driver, 10).until(
            lambda d: len(d.find_elements(By.TAG_NAME, "tr")) > 0 and 
                     d.find_element(By.ID, "jobsTableBody").text.strip() != ''
        )
        
        # Print table contents for debugging
        table = driver.find_element(By.ID, "jobsTableBody")
        print(f"Table HTML: {table.get_attribute('innerHTML')}")
        
        # Print console logs
        logs = driver.get_log('browser')
        print("Browser logs:")
        for log in logs:
            print(log)
        
        # Find the first resume button
        buttons = driver.find_elements(By.CLASS_NAME, "resume-button")
        assert len(buttons) > 0, "No resume buttons found"
        button = buttons[0]
        
        # Get the job ID
        row = button.find_element(By.XPATH, "./ancestor::tr")
        job_id = row.get_attribute('data-job-id')
        
        # Click the button
        button.click()
        
        # Wait for the button to change to a link
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, f'tr[data-job-id="{job_id}"] .resume-button.tailored'))
        )
        
        # Verify the link
        link = driver.find_element(By.CSS_SELECTOR, f'tr[data-job-id="{job_id}"] .resume-button.tailored')
        assert "Tailored Resume" in link.text
        assert link.get_attribute('href').endswith(f'tailored-resume.html?jobId={job_id}')
        
    except Exception as e:
        print(f"Error in test: {str(e)}")
        # Print current page source
        print(f"Page source at error: {driver.page_source}")
        raise e

def test_database_operations(test_db):
    conn = sqlite3.connect(test_db)
    cursor = conn.cursor()
    
    # Test job exists
    cursor.execute('SELECT * FROM jobs WHERE company = ?', ('Test Company',))
    job = cursor.fetchone()
    assert job is not None
    
    # Create tailored resume
    cursor.execute('''
        INSERT INTO tailored_resumes (job_id, content)
        VALUES (?, ?)
    ''', (job[0], 'Test tailored resume content'))
    conn.commit()
    
    # Test tailored resume exists
    cursor.execute('''
        SELECT * FROM tailored_resumes 
        WHERE job_id = ?
    ''', (job[0],))
    resume = cursor.fetchone()
    assert resume is not None
    assert resume[2] == 'Test tailored resume content'
    
    conn.close()

if __name__ == '__main__':
    pytest.main([__file__]) 