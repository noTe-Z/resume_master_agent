#!/usr/bin/env python3
"""
Debug script for testing section identification in resumes.
"""

import os
import sys
import json

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from backend.resume_parser.parser import normalize_text, identify_sections

def main():
    # Test with the sample resume
    test_file = os.path.join(os.path.dirname(__file__), 'resume_parser', 'fixtures', 'sample_resume.txt')
    
    with open(test_file, 'r') as f:
        content = f.read()
    
    # Print original content (first 200 chars)
    print(f"Original content preview:\n{content[:200]}...\n")
    
    # Normalize text
    normalized = normalize_text(content)
    print(f"Normalized content preview:\n{normalized[:200]}...\n")
    
    # Identify sections
    sections = identify_sections(normalized)
    
    # Print identified sections
    print("Identified Sections:")
    for section, content in sections.items():
        content_preview = content[:50] + "..." if content and len(content) > 50 else content
        print(f"  - {section}: {content_preview}")

if __name__ == "__main__":
    main() 