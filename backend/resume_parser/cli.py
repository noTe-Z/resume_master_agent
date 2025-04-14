#!/usr/bin/env python3
"""
Resume Parser CLI

Command-line tool for testing the resume parser with different files.
"""

import os
import sys
import json
import argparse
import logging
from typing import Dict, Any

# Add the project root to the Python path to allow imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from backend.resume_parser.interface import parse_resume, save_parsed_resume

# Initialize logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description='Parse resume files into structured data.')
    parser.add_argument('file_path', help='Path to the resume file (PDF, DOC, or DOCX)')
    parser.add_argument('--output', '-o', help='Path to save the parsed resume data (JSON)')
    parser.add_argument('--pretty', '-p', action='store_true', help='Pretty-print the output')
    parser.add_argument('--verbose', '-v', action='store_true', help='Increase output verbosity')
    return parser.parse_args()

def main():
    """Main entry point for the CLI."""
    args = parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Check if file exists
        if not os.path.exists(args.file_path):
            logger.error(f"File not found: {args.file_path}")
            sys.exit(1)
        
        # Parse resume
        logger.info(f"Parsing resume: {args.file_path}")
        resume_data = parse_resume(args.file_path)
        
        # Check for errors
        if 'error' in resume_data:
            logger.error(f"Error parsing resume: {resume_data['error']}")
            sys.exit(1)
        
        # Save to file if output path is provided
        if args.output:
            logger.info(f"Saving parsed resume data to {args.output}")
            if save_parsed_resume(resume_data, args.output):
                logger.info("Data saved successfully")
            else:
                logger.error("Failed to save data")
                sys.exit(1)
        
        # Print to stdout
        if args.pretty:
            print(json.dumps(resume_data, indent=2))
        else:
            print(json.dumps(resume_data))
        
        logger.info("Resume parsing completed successfully")
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 