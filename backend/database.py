import sqlite3
from datetime import datetime
from typing import List, Dict, Optional

class Database:
    def __init__(self, db_path: str = "jobs.db"):
        self.db_path = db_path
        self.create_tables()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def create_tables(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        # Create jobs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                company TEXT NOT NULL,
                description TEXT NOT NULL,
                apply_link TEXT,
                saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()

    def save_job(self, title: str, company: str, description: str, apply_link: Optional[str] = None) -> int:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO jobs (title, company, description, apply_link) VALUES (?, ?, ?, ?)",
            (title, company, description, apply_link)
        )
        job_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        return job_id

    def get_jobs(self) -> List[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM jobs ORDER BY saved_at DESC")
        jobs = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return jobs

    def get_job(self, job_id: int) -> Optional[Dict]:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
        job = cursor.fetchone()
        
        conn.close()
        return dict(job) if job else None

    def delete_job(self, job_id: int) -> bool:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
        success = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        return success 