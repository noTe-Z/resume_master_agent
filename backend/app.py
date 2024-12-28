import os
import json
import sqlite3
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, date

app = Flask(__name__)
CORS(app)

def get_db():
    db = sqlite3.connect('jobs.db')
    db.row_factory = sqlite3.Row
    return db

def init_db():
    with get_db() as db:
        # Drop existing jobs table if it exists to ensure clean schema
        db.execute('DROP TABLE IF EXISTS jobs')
        db.execute('''
            CREATE TABLE jobs (
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
        today_count = get_today_stats()
        daily_goal = 10  # Current daily application goal
        return jsonify({
            'today_applied': today_count,
            'daily_goal': daily_goal,
            'goal_met': today_count >= daily_goal
        }), 200
    except Exception as e:
        print(f"Error getting today's job stats: {e}")
        return jsonify({'error': str(e)}), 500

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
            jobs = db.execute('SELECT * FROM jobs ORDER BY saved_at DESC').fetchall()
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

if __name__ == '__main__':
    init_db()
    app.run(port=3000) 