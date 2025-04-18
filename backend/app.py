import os
import json
import sys
import sqlite3
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime, date

# Resume parser imports
from resume_parser.file_handler import save_resume_file
from resume_parser.interface import parse_resume, save_parsed_resume

# Get the absolute path to the extension/popup directory
STATIC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'extension', 'popup'))

app = Flask(__name__)
CORS(app)

def get_db():
    db = sqlite3.connect('jobs.db')
    db.row_factory = sqlite3.Row
    return db

def init_db():
    with get_db() as db:
        # Only create table if it doesn't exist
        db.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                company TEXT NOT NULL,
                description TEXT,
                apply_link TEXT,
                status TEXT CHECK(status IN ('to_apply', 'applied', 'interviewing')) DEFAULT 'to_apply',
                saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                applied_at TIMESTAMP
            )
        ''')
        
        # Create tailored resumes table
        db.execute('''
            CREATE TABLE IF NOT EXISTS tailored_resumes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
            )
        ''')
        
        # Check if we need to add the applied_at column (for backward compatibility)
        columns = db.execute("PRAGMA table_info(jobs)").fetchall()
        column_names = [col[1] for col in columns]
        
        if 'applied_at' not in column_names:
            db.execute('ALTER TABLE jobs ADD COLUMN applied_at TIMESTAMP')
            
        if 'status' not in column_names:
            db.execute('ALTER TABLE jobs ADD COLUMN status TEXT DEFAULT "to_apply"')
            
        db.commit()

def get_status_counts():
    with get_db() as db:
        counts = db.execute('''
            SELECT status, COUNT(*) as count
            FROM jobs
            GROUP BY status
        ''').fetchall()
        return {row['status']: row['count'] for row in counts}

def get_today_stats():
    today = date.today().isoformat()
    with get_db() as db:
        count = db.execute('''
            SELECT COUNT(*) as count
            FROM jobs
            WHERE status = 'applied'
            AND date(applied_at) = ?
        ''', (today,)).fetchone()['count']
        return count

@app.route('/jobs/today-stats', methods=['GET'])
def get_today_job_stats():
    try:
        today_count = get_today_stats() or 0  # Ensure we return 0 if None
        daily_goal = 10  # Current daily application goal
        return jsonify({
            'today_applied': today_count,
            'daily_goal': daily_goal,
            'goal_met': today_count >= daily_goal
        }), 200
    except Exception as e:
        print(f"Error getting today's job stats: {e}")
        # Return a proper error response with 500 status
        return jsonify({
            'today_applied': 0,
            'daily_goal': 10,
            'goal_met': False,
            'error': str(e)
        }), 200  # Return 200 with default values instead of 500

@app.route('/jobs/stats', methods=['GET'])
def get_job_stats():
    try:
        counts = get_status_counts()
        return jsonify({
            'total': sum(counts.values()),
            'by_status': counts
        }), 200
    except Exception as e:
        print(f"Error getting job stats: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/save-job', methods=['POST'])
def save_job():
    try:
        data = request.json
        title = data.get('title')
        company = data.get('company')
        description = data.get('description')
        apply_link = data.get('apply_link')
        
        if not title or not company:
            return jsonify({'error': 'Missing required fields'}), 400
            
        with get_db() as db:
            cursor = db.execute(
                'INSERT INTO jobs (title, company, description, apply_link) VALUES (?, ?, ?, ?)',
                (title, company, description, apply_link)
            )
            job_id = cursor.lastrowid
            db.commit()
            
        return jsonify({'message': 'Job saved successfully', 'id': job_id}), 200
        
    except Exception as e:
        print(f"Error saving job: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/jobs', methods=['GET'])
@app.route('/get-jobs', methods=['GET'])
def get_jobs():
    try:
        with get_db() as db:
            # Get jobs with tailored resume information
            jobs = db.execute('''
                SELECT j.*, 
                       CASE WHEN tr.id IS NOT NULL THEN 1 ELSE 0 END as has_tailored_resume
                FROM jobs j
                LEFT JOIN (
                    SELECT DISTINCT job_id, MIN(id) as id
                    FROM tailored_resumes
                    GROUP BY job_id
                ) tr ON j.id = tr.job_id
                ORDER BY j.saved_at DESC
            ''').fetchall()
            
            # Convert to dict and ensure no null values
            processed_jobs = []
            for job in jobs:
                job_dict = dict(job)
                # Replace None values with empty strings
                for key in job_dict:
                    if job_dict[key] is None:
                        job_dict[key] = ''
                processed_jobs.append(job_dict)
            return jsonify(processed_jobs), 200
            
    except Exception as e:
        print(f"Error getting jobs: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/jobs/<int:job_id>/status', methods=['PUT'])
def update_job_status(job_id):
    try:
        data = request.json
        new_status = data.get('status')
        
        if not new_status or new_status not in ['to_apply', 'applied', 'interviewing']:
            return jsonify({'error': 'Invalid status'}), 400
            
        with get_db() as db:
            # First, get the current status
            current = db.execute('SELECT status FROM jobs WHERE id = ?', (job_id,)).fetchone()
            if not current:
                return jsonify({'error': 'Job not found'}), 404

            if new_status == 'applied':
                # Set applied_at timestamp when changing to applied
                db.execute('''
                    UPDATE jobs 
                    SET status = ?, applied_at = CURRENT_TIMESTAMP 
                    WHERE id = ?
                ''', (new_status, job_id))
            else:
                # Clear applied_at timestamp when changing from applied to another status
                db.execute('''
                    UPDATE jobs 
                    SET status = ?, 
                        applied_at = CASE 
                            WHEN status = 'applied' THEN NULL 
                            ELSE applied_at 
                        END
                    WHERE id = ?
                ''', (new_status, job_id))
            db.commit()
            
        return jsonify({'message': 'Status updated successfully'}), 200
        
    except Exception as e:
        print(f"Error updating job status: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/delete-job/<int:job_id>', methods=['DELETE'])
def delete_job(job_id):
    try:
        with get_db() as db:
            db.execute('DELETE FROM jobs WHERE id = ?', (job_id,))
            db.commit()
        return jsonify({'message': 'Job deleted successfully'}), 200
        
    except Exception as e:
        print(f"Error deleting job: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/jobs/<int:job_id>/tailor-resume', methods=['POST'])
def tailor_resume(job_id):
    try:
        with get_db() as db:
            # Get job details
            job = db.execute('SELECT * FROM jobs WHERE id = ?', (job_id,)).fetchone()
            if not job:
                return jsonify({'error': 'Job not found'}), 404
            
            # Get the absolute path to resume_experience_chunk.tex
            resume_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'resume_experience_chunk.tex'))
            
            # Check if file exists
            if not os.path.exists(resume_path):
                return jsonify({'error': 'Resume template not found'}), 404
            
            # Read resume content
            try:
                with open(resume_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                if not content:
                    return jsonify({'error': 'Resume template is empty'}), 500
            except Exception as e:
                print(f"Error reading resume file: {e}")
                return jsonify({'error': 'Failed to read resume template'}), 500
            
            # Store the tailored resume in a transaction
            try:
                # Start transaction
                db.execute('BEGIN')
                
                # Store the tailored resume
                cursor = db.execute(
                    'INSERT INTO tailored_resumes (job_id, content) VALUES (?, ?)',
                    (job_id, content)
                )
                resume_id = cursor.lastrowid
                
                # Commit transaction
                db.commit()
                
                # Get the updated job data with has_tailored_resume status
                updated_job = db.execute('''
                    SELECT j.*, 
                           CASE WHEN tr.id IS NOT NULL THEN 1 ELSE 0 END as has_tailored_resume
                    FROM jobs j
                    LEFT JOIN (
                        SELECT DISTINCT job_id, MIN(id) as id
                        FROM tailored_resumes
                        GROUP BY job_id
                    ) tr ON j.id = tr.job_id
                    WHERE j.id = ?
                ''', (job_id,)).fetchone()
                
                return jsonify({
                    'message': 'Resume tailored successfully',
                    'resume_id': resume_id,
                    'job': dict(updated_job)
                }), 200
                
            except Exception as e:
                # Rollback transaction on error
                db.execute('ROLLBACK')
                raise e
                
    except Exception as e:
        print(f"Error tailoring resume: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/jobs/<int:job_id>/tailored-resume', methods=['GET'])
def get_tailored_resume(job_id):
    try:
        with get_db() as db:
            # Get the most recent tailored resume for this job
            resume = db.execute('''
                SELECT * FROM tailored_resumes 
                WHERE job_id = ? 
                ORDER BY created_at DESC 
                LIMIT 1
            ''', (job_id,)).fetchone()
            
            if not resume:
                return jsonify({'error': 'No tailored resume found'}), 404
                
            return jsonify({
                'id': resume['id'],
                'content': resume['content'],
                'created_at': resume['created_at']
            }), 200
            
    except Exception as e:
        print(f"Error getting tailored resume: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/jobs/<int:job_id>', methods=['GET'])
def get_job(job_id):
    try:
        with get_db() as db:
            # Get job with tailored resume information
            job = db.execute('''
                SELECT j.*, 
                       CASE WHEN tr.id IS NOT NULL THEN 1 ELSE 0 END as has_tailored_resume
                FROM jobs j
                LEFT JOIN (
                    SELECT DISTINCT job_id, MIN(id) as id
                    FROM tailored_resumes
                    GROUP BY job_id
                ) tr ON j.id = tr.job_id
                WHERE j.id = ?
            ''', (job_id,)).fetchone()
            
            if not job:
                return jsonify({'error': 'Job not found'}), 404
                
            job_dict = dict(job)
            # Replace None values with empty strings
            for key in job_dict:
                if job_dict[key] is None:
                    job_dict[key] = ''
            return jsonify(job_dict), 200
            
    except Exception as e:
        print(f"Error getting job: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/')
def index():
    return send_from_directory(STATIC_DIR, 'jobs.html')

@app.route('/resume-editor')
def resume_editor():
    return send_from_directory(STATIC_DIR, 'resume-editor.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(STATIC_DIR, path)

# Resume parsing endpoint
@app.route('/parse-resume', methods=['POST'])
def parse_resume_endpoint():
    try:
        print("Received resume parsing request")
        
        # Check if the post request has the file part
        if 'file' not in request.files:
            print("No file part in the request")
            return jsonify({'error': 'No file part'}), 400
            
        file = request.files['file']
        print(f"File received: {file.filename}, Content type: {file.content_type}")
        
        # If user does not select file, browser might submit an empty file
        if file.filename == '':
            print("Empty filename")
            return jsonify({'error': 'No selected file'}), 400
            
        # Save the uploaded file
        print(f"Saving file: {file.filename}")
        success, message, file_path = save_resume_file(file)
        
        if not success:
            print(f"Failed to save file: {message}")
            return jsonify({'error': message}), 400
        
        print(f"Successfully saved resume file to {file_path}")
            
        # Parse the resume
        # First try the enhanced parser if the file is PDF
        if file_path.lower().endswith('.pdf'):
            try:
                print(f"Attempting to use enhanced parser for {file_path}")
                # Import the enhanced parser from the resume_parser module
                from resume_parser import enhanced_parse_resume
                
                # Parse with enhanced parser
                print(f"Running enhanced parser on {file_path}")
                resume_data = enhanced_parse_resume(file_path)
                
                # Check if any data was returned
                if resume_data and isinstance(resume_data, dict) and 'contact_info' in resume_data:
                    print(f"Enhanced parser successful for {file_path}")
                    print(f"Resume data keys: {resume_data.keys()}")
                    # Save the parsed data for future reference
                    data_path = os.path.join(os.path.dirname(file_path), f"{os.path.splitext(os.path.basename(file_path))[0]}.json")
                    save_parsed_resume(resume_data, data_path)
                    
                    return jsonify({
                        'success': True,
                        'message': 'Resume parsed successfully with enhanced parser',
                        'data': resume_data
                    }), 200
                else:
                    print(f"Enhanced parser didn't return valid data for {file_path}")
                    if resume_data and isinstance(resume_data, dict) and 'error' in resume_data:
                        print(f"Parser error: {resume_data['error']}")
            except Exception as e:
                print(f"Enhanced parser error: {str(e)}")
                import traceback
                traceback.print_exc()
        else:
            print(f"File {file_path} is not a PDF, skipping enhanced parser")
        
        # Fallback to the regular parser
        print(f"Using standard parser for {file_path}")
        resume_data = parse_resume(file_path)
        
        # Check for errors in parsing
        if 'error' in resume_data:
            print(f"Standard parser error: {resume_data['error']}")
            return jsonify({'error': resume_data['error']}), 500
            
        # Save the parsed data for future reference
        data_path = os.path.join(os.path.dirname(file_path), f"{os.path.splitext(os.path.basename(file_path))[0]}.json")
        save_parsed_resume(resume_data, data_path)
        
        print("Standard parser succeeded")
        return jsonify({
            'success': True,
            'message': 'Resume parsed successfully',
            'data': resume_data
        }), 200
            
    except Exception as e:
        print(f"Error parsing resume: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/test-resume-parser', methods=['GET'])
def test_resume_parser():
    try:
        # Get the absolute path to test PDF file
        test_resume_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'example_resumes', 'test_resume.pdf'))
        
        # Check if file exists
        if not os.path.exists(test_resume_path):
            return jsonify({'error': 'Test resume file not found'}), 404
        
        # Import the enhanced parser from the resume_parser module
        from resume_parser import enhanced_parse_resume
        
        # Parse with enhanced parser
        resume_data = enhanced_parse_resume(test_resume_path)
        
        return jsonify({
            'success': True,
            'message': 'Resume parsed successfully with enhanced parser',
            'data': resume_data
        }), 200
            
    except Exception as e:
        print(f"Error testing resume parser: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/test-upload-form')
def test_upload_form():
    return '''
    <!doctype html>
    <html>
    <head>
        <title>Resume Upload Test</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }
            .form-group {
                margin-bottom: 15px;
            }
            .button {
                background-color: #4CAF50;
                color: white;
                padding: 10px 15px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
            }
            #result {
                margin-top: 20px;
                padding: 15px;
                border: 1px solid #ddd;
                border-radius: 4px;
                white-space: pre-wrap;
                display: none;
            }
        </style>
    </head>
    <body>
        <h1>Resume Upload Test</h1>
        <form id="uploadForm" enctype="multipart/form-data">
            <div class="form-group">
                <label for="resume">Select a PDF resume:</label>
                <input type="file" id="resume" name="file" accept=".pdf,.docx,.doc">
            </div>
            <button type="submit" class="button">Parse Resume</button>
        </form>
        <div id="result"></div>
        
        <script>
            document.getElementById('uploadForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const formData = new FormData();
                const fileInput = document.getElementById('resume');
                const resultDiv = document.getElementById('result');
                
                if (fileInput.files.length === 0) {
                    alert('Please select a file first.');
                    return;
                }
                
                formData.append('file', fileInput.files[0]);
                
                try {
                    resultDiv.innerHTML = 'Parsing resume...';
                    resultDiv.style.display = 'block';
                    
                    const response = await fetch('/parse-resume', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        let formattedResult = JSON.stringify(data, null, 2);
                        resultDiv.innerHTML = `<h3>Parsing Result:</h3><pre>${formattedResult}</pre>`;
                    } else {
                        resultDiv.innerHTML = `<h3>Error:</h3><p>${data.error || 'Unknown error'}</p>`;
                    }
                } catch (error) {
                    resultDiv.innerHTML = `<h3>Error:</h3><p>${error.message || 'Failed to parse resume'}</p>`;
                }
            });
        </script>
    </body>
    </html>
    '''

if __name__ == '__main__':
    init_db()
    app.run(port=5000) 