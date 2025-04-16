#!/usr/bin/env python3
"""
Test script for the enhanced resume parser.
"""

import os
import sys
import unittest
import json
from fpdf import FPDF

# Add parent directory to path to allow importing from backend
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from backend.resume_parser.enhanced_parser import parse_resume

class TestEnhancedResumeParser(unittest.TestCase):
    """Test cases for the enhanced resume parser."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test data once before all test methods are run."""
        # Create a test directory if it doesn't exist
        cls.test_dir = os.path.join(os.path.dirname(__file__), 'test_data')
        os.makedirs(cls.test_dir, exist_ok=True)
        
        # Create a test PDF resume
        cls.test_resume_path = os.path.join(cls.test_dir, 'test_resume.pdf')
        cls._create_test_resume(cls.test_resume_path)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests are run."""
        # Remove test resume file
        if os.path.exists(cls.test_resume_path):
            os.remove(cls.test_resume_path)
    
    @staticmethod
    def _create_test_resume(output_path):
        """Create a test PDF resume."""
        pdf = FPDF()
        pdf.add_page()
        
        # Set font for header content
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'John Doe', ln=True, align='C')
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 8, 'john.doe@example.com | 555-123-4567', ln=True, align='C')
        pdf.cell(0, 8, 'New York, NY | linkedin.com/in/johndoe', ln=True, align='C')
        pdf.ln(10)
        
        # SUMMARY section
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'SUMMARY', ln=True)
        pdf.set_font('Arial', '', 12)
        pdf.multi_cell(0, 8, 'Experienced software engineer with expertise in web development.')
        pdf.ln(5)
        
        # EXPERIENCE section
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'EXPERIENCE', ln=True)
        
        # First job
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, 'ABC Company, Software Engineer', ln=True)
        pdf.set_font('Arial', 'I', 10)
        pdf.cell(0, 8, 'January 2018 - December 2022', ln=True)
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 8, '- Developed web applications using React', ln=True)
        pdf.cell(0, 8, '- Implemented RESTful APIs', ln=True)
        pdf.ln(5)
        
        # EDUCATION section
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'EDUCATION', ln=True)
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, 'University of Example, BS Computer Science', ln=True)
        pdf.set_font('Arial', 'I', 10)
        pdf.cell(0, 8, '2014 - 2018', ln=True)
        pdf.ln(5)
        
        # SKILLS section
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'SKILLS', ln=True)
        pdf.set_font('Arial', '', 12)
        pdf.multi_cell(0, 8, 'JavaScript, React, Node.js, Python, SQL')
        
        # Save the pdf file
        pdf.output(output_path)
    
    def test_parse_resume(self):
        """Test parsing a resume."""
        # Parse the test resume
        result = parse_resume(self.test_resume_path)
        
        # Check that result is a dictionary
        self.assertIsInstance(result, dict)
        
        # Check that contact info was extracted
        self.assertIn('contact_info', result)
        contact_info = result['contact_info']
        self.assertEqual(contact_info.get('name'), 'John Doe')
        self.assertEqual(contact_info.get('email'), 'john.doe@example.com')
        self.assertEqual(contact_info.get('phone'), '555-123-4567')
        self.assertEqual(contact_info.get('linkedin'), 'linkedin.com/in/johndoe')
        
        # Check that experiences were extracted
        self.assertIn('experiences', result)
        experiences = result['experiences']
        self.assertIsInstance(experiences, list)
        
        # Print the result for debugging
        print("Parse result:")
        print(json.dumps(result, indent=2))

if __name__ == '__main__':
    unittest.main() 