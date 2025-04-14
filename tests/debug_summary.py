#!/usr/bin/env python3
"""
Debug script for testing summary section identification.
"""

import os
import sys
import re

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from backend.resume_parser.parser import normalize_text, identify_sections, SECTION_HEADERS

def debug_section_headers(text):
    lines = text.split('\n')
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
            
        line_lower = line.lower()
        
        # Check for uppercase section headers
        if line.isupper() and len(line) >= 3:
            print(f"Line {i}: '{line}' is uppercase")
            for section, headers in SECTION_HEADERS.items():
                if any(header.upper() == line_lower.upper() for header in headers):
                    print(f"  - Matches section: {section}")
        
        # Check for regular section headers
        for section, headers in SECTION_HEADERS.items():
            if any(re.search(r'\b' + re.escape(header) + r'\b', line_lower, re.IGNORECASE) for header in headers):
                print(f"Line {i}: '{line}' matches section: {section} (case insensitive)")

def main():
    # Test with the sample resume
    test_file = os.path.join(os.path.dirname(__file__), 'resume_parser', 'fixtures', 'sample_resume.txt')
    
    with open(test_file, 'r') as f:
        content = f.read()
    
    # Normalize text
    normalized = normalize_text(content)
    
    # Debug section headers
    print("Analyzing section headers:")
    debug_section_headers(normalized)
    
    # Print line by line with indices
    print("\nDocument line by line:")
    for i, line in enumerate(normalized.split('\n')):
        print(f"{i}: '{line}'")

if __name__ == "__main__":
    main() 