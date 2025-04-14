"""
Resume Parser Interface

This module provides a unified interface for parsing different resume file formats.
"""

import os
import logging
from typing import Dict, Any, Optional

from backend.resume_parser.file_handler import get_file_extension
from backend.resume_parser.parser import parse_resume_pdf
from backend.resume_parser.docx_parser import parse_resume_docx

# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_resume(file_path: str) -> Dict[str, Any]:
    """
    Parse a resume file into structured data.
    
    This function determines the file type and calls the appropriate parser.
    
    Args:
        file_path: Path to the resume file
        
    Returns:
        Dictionary containing structured resume data
    """
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return {'error': 'File not found'}
        
        # Get file extension
        file_ext = get_file_extension(file_path)
        
        # Call appropriate parser based on file extension
        if file_ext == 'pdf':
            logger.info(f"Parsing PDF resume: {file_path}")
            return parse_resume_pdf(file_path)
        elif file_ext in ['docx', 'doc']:
            logger.info(f"Parsing DOCX resume: {file_path}")
            return parse_resume_docx(file_path)
        else:
            logger.error(f"Unsupported file format: {file_ext}")
            return {'error': f'Unsupported file format: {file_ext}'}
    except Exception as e:
        logger.error(f"Error parsing resume: {str(e)}")
        return {'error': str(e)}

def save_parsed_resume(resume_data: Dict[str, Any], file_path: Optional[str] = None) -> bool:
    """
    Save parsed resume data for future use.
    
    Args:
        resume_data: Structured resume data
        file_path: Optional path to save the data (if not provided, a default path will be used)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        import json
        
        # Create a default path if not provided
        if not file_path:
            # Generate filename from contact info if available
            name = resume_data.get('contact_info', {}).get('name', 'unnamed')
            name = name.lower().replace(' ', '_')
            file_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', f"{name}_resume.json")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Save as JSON
        with open(file_path, 'w') as f:
            json.dump(resume_data, f, indent=2)
        
        logger.info(f"Parsed resume data saved to {file_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving parsed resume data: {str(e)}")
        return False

def load_parsed_resume(file_path: str) -> Dict[str, Any]:
    """
    Load previously parsed resume data.
    
    Args:
        file_path: Path to the saved resume data
        
    Returns:
        Dictionary containing structured resume data
    """
    try:
        import json
        
        # Check if file exists
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return {'error': 'File not found'}
        
        # Load JSON
        with open(file_path, 'r') as f:
            resume_data = json.load(f)
        
        logger.info(f"Parsed resume data loaded from {file_path}")
        return resume_data
    except Exception as e:
        logger.error(f"Error loading parsed resume data: {str(e)}")
        return {'error': str(e)} 