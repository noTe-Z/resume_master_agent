import os
import json
import sqlite3
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

def get_db():
    db = sqlite3.connect('jobs.db')
    db.row_factory = sqlite3.Row
    return db

def init_db():
    with get_db() as db:
        db.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                company TEXT NOT NULL,
                description TEXT,
                apply_link TEXT,
                saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        db.commit()

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

@app.route('/get-jobs', methods=['GET'])
def get_jobs():
    try:
        with get_db() as db:
            jobs = db.execute('SELECT * FROM jobs ORDER BY saved_at DESC').fetchall()
            return jsonify([dict(job) for job in jobs]), 200
            
    except Exception as e:
        print(f"Error getting jobs: {e}")
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