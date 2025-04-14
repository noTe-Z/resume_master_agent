"""
Resume File Handler

This module provides functions for handling uploaded resume files.
"""

import os
import uuid
import logging
from typing import Tuple, Optional
from werkzeug.utils import secure_filename

# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc'}

# Set upload directory
UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'uploads'))

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_DIR, exist_ok=True)

def allowed_file(filename: str) -> bool:
    """
    Check if a file has an allowed extension.
    
    Args:
        filename: The name of the file to check
        
    Returns:
        True if the file has an allowed extension, False otherwise
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_resume_file(file, user_id: str = None) -> Tuple[bool, str, Optional[str]]:
    """
    Save an uploaded resume file to disk.
    
    Args:
        file: The file object from the request
        user_id: Optional user ID to associate with the file
        
    Returns:
        Tuple containing:
        - Success status (True/False)
        - Message string
        - Path to the saved file (if successful, otherwise None)
    """
    try:
        if file and allowed_file(file.filename):
            # Generate a secure filename
            filename = secure_filename(file.filename)
            
            # Add user_id prefix if provided
            prefix = f"{user_id}_" if user_id else ""
            
            # Add a UUID to ensure uniqueness
            unique_filename = f"{prefix}{uuid.uuid4().hex}_{filename}"
            
            # Full path to save the file
            file_path = os.path.join(UPLOAD_DIR, unique_filename)
            
            # Save the file
            file.save(file_path)
            
            logger.info(f"Resume file saved successfully: {file_path}")
            return True, "File uploaded successfully", file_path
        else:
            logger.warning(f"Invalid file type: {file.filename if file else 'No file'}")
            return False, "Invalid file type. Please upload a PDF, DOC, or DOCX file.", None
    except Exception as e:
        logger.error(f"Error saving resume file: {str(e)}")
        return False, f"Error saving file: {str(e)}", None

def delete_resume_file(file_path: str) -> Tuple[bool, str]:
    """
    Delete a resume file from disk.
    
    Args:
        file_path: Path to the file to delete
        
    Returns:
        Tuple containing:
        - Success status (True/False)
        - Message string
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Resume file deleted successfully: {file_path}")
            return True, "File deleted successfully"
        else:
            logger.warning(f"File not found: {file_path}")
            return False, "File not found"
    except Exception as e:
        logger.error(f"Error deleting resume file: {str(e)}")
        return False, f"Error deleting file: {str(e)}"

def get_file_extension(file_path: str) -> str:
    """
    Get the extension of a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        File extension (without the dot)
    """
    return os.path.splitext(file_path)[1][1:].lower() 