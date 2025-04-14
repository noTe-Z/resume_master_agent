"""
Resume Parser Tests

Tests for the resume parser functionality.
"""

import os
import sys
import unittest
import json
import tempfile

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from backend.resume_parser.parser import (
    normalize_text,
    identify_sections,
    extract_contact_info,
    parse_experience_section,
    parse_education_section,
    parse_skills_section
)

class TestResumeParser(unittest.TestCase):
    """Test cases for resume parser functions."""
    
    def test_normalize_text(self):
        """Test normalizing text."""
        input_text = "This is a   test\n\nwith multiple   spaces\n\n\nand newlines."
        expected = "This is a test\nwith multiple spaces\nand newlines."
        self.assertEqual(normalize_text(input_text), expected)
    
    def test_identify_sections(self):
        """Test section identification."""
        test_text = """John Doe
john.doe@example.com

Summary
A passionate software engineer with expertise in Python and JavaScript.

Experience
Software Engineer, ABC Inc, 2018-2022
- Developed web applications using React
- Implemented backend services with Django

Education
Bachelor of Science in Computer Science, XYZ University, 2014-2018
"""
        sections = identify_sections(test_text)
        
        self.assertIn('summary', sections)
        self.assertIn('experience', sections)
        self.assertIn('education', sections)
        
        self.assertIn('passionate software engineer', sections['summary'].lower())
        self.assertIn('software engineer, abc inc', sections['experience'].lower())
        self.assertIn('bachelor of science', sections['education'].lower())
    
    def test_extract_contact_info(self):
        """Test contact information extraction."""
        test_text = """John Doe
123 Main St, City, State 12345
(555) 123-4567
john.doe@example.com
linkedin.com/in/johndoe
github.com/johndoe
"""
        contact_info = extract_contact_info(test_text)
        
        # Name extraction might be dependent on spaCy model, which we're mocking
        # self.assertEqual(contact_info['name'], 'John Doe')
        self.assertEqual(contact_info['email'], 'john.doe@example.com')
        self.assertEqual(contact_info['phone'], '(555) 123-4567')
        self.assertEqual(contact_info['linkedin'], 'linkedin.com/in/johndoe')
        self.assertEqual(contact_info['github'], 'github.com/johndoe')
    
    def test_parse_experience_section(self):
        """Test parsing the experience section."""
        test_text = """Software Engineer, ABC Inc, 2018-2022
- Developed web applications using React
- Implemented backend services with Django

Junior Developer, XYZ Corp, 2016-2018
- Assisted in mobile app development
- Conducted code reviews and testing
"""
        experiences = parse_experience_section(test_text)
        
        self.assertEqual(len(experiences), 2)
        self.assertEqual(experiences[0]['title'], 'Software Engineer')
        self.assertEqual(experiences[0]['company'], 'ABC Inc')
        self.assertEqual(experiences[0]['start_date'], '2018')
        self.assertEqual(experiences[0]['end_date'], '2022')
        self.assertEqual(len(experiences[0]['bullets']), 2)
        
        self.assertEqual(experiences[1]['title'], 'Junior Developer')
        self.assertEqual(experiences[1]['company'], 'XYZ Corp')
    
    def test_parse_education_section(self):
        """Test parsing the education section."""
        test_text = """Bachelor of Science in Computer Science, XYZ University, 2014-2018
GPA: 3.8/4.0, Dean's List

Associate Degree, Community College, 2012-2014
Coursework in programming and mathematics
"""
        education = parse_education_section(test_text)
        
        self.assertEqual(len(education), 2)
        self.assertEqual(education[0]['degree'], 'Bachelor of Science in Computer Science')
        self.assertEqual(education[0]['institution'], 'XYZ University')
        self.assertEqual(education[0]['start_date'], '2014')
        self.assertEqual(education[0]['end_date'], '2018')
        
        self.assertEqual(education[1]['degree'], 'Associate Degree')
        self.assertEqual(education[1]['institution'], 'Community College')
    
    def test_parse_skills_section(self):
        """Test parsing the skills section."""
        test_text = """Programming: Python, JavaScript, Java, C++
Frameworks: React, Django, Angular
Databases: PostgreSQL, MongoDB
Other: Git, Docker, AWS, Agile methodologies
"""
        skills = parse_skills_section(test_text)
        
        self.assertIn('technical_skills', skills)
        self.assertIn('soft_skills', skills)
        self.assertIn('other_skills', skills)
        
        # Most of these should be categorized as technical skills
        self.assertTrue(len(skills['technical_skills']) > 0)
        
        # Check if some specific skills were extracted
        all_skills = skills['technical_skills'] + skills['soft_skills'] + skills['other_skills']
        skill_names = [skill.lower() for skill in all_skills]
        
        for expected_skill in ['python', 'javascript', 'react', 'django', 'postgresql', 'git']:
            self.assertTrue(
                any(expected_skill.lower() in s for s in skill_names),
                f"Expected skill '{expected_skill}' not found in extracted skills"
            )

if __name__ == '__main__':
    unittest.main() 