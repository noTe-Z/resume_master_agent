"""
Resume Parser Integration Tests

This module tests the integration of different components in the resume parser.
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
    parse_skills_section,
    extract_certifications
)

class TestResumeParserIntegration(unittest.TestCase):
    """Integration tests for the resume parser."""
    
    def setUp(self):
        """Set up the test fixtures."""
        fixture_path = os.path.join(os.path.dirname(__file__), 'fixtures', 'sample_resume.txt')
        with open(fixture_path, 'r') as f:
            self.sample_resume_text = f.read()
    
    def test_end_to_end_parsing(self):
        """Test the entire parsing pipeline with the sample resume."""
        # Normalize the text
        normalized_text = normalize_text(self.sample_resume_text)
        
        # Identify sections
        sections = identify_sections(normalized_text)
        
        # Extract contact information
        contact_info = extract_contact_info(sections.get('other', '') or normalized_text[:500])
        
        # Parse experience section
        experiences = parse_experience_section(sections.get('experience', ''))
        
        # Parse education section
        education = parse_education_section(sections.get('education', ''))
        
        # Parse skills section
        skills = parse_skills_section(sections.get('skills', ''))
        
        # Extract certifications
        certifications = extract_certifications(sections.get('certifications', ''))
        
        # Validate contact info
        self.assertEqual(contact_info['email'], 'john.doe@example.com')
        self.assertEqual(contact_info['phone'], '(555) 123-4567')
        self.assertEqual(contact_info['linkedin'], 'linkedin.com/in/johndoe')
        self.assertEqual(contact_info['github'], 'github.com/johndoe')
        
        # Validate sections
        self.assertIn('summary', sections)
        self.assertIn('experience', sections)
        self.assertIn('education', sections)
        self.assertIn('skills', sections)
        self.assertIn('certifications', sections)
        self.assertIn('projects', sections)
        self.assertIn('languages', sections)
        self.assertIn('interests', sections)
        
        # Validate experiences
        self.assertGreaterEqual(len(experiences), 2)
        
        senior_eng = next((exp for exp in experiences if 'senior software engineer' in exp['title'].lower()), None)
        self.assertIsNotNone(senior_eng)
        self.assertIn('tech solutions', senior_eng['company'].lower())
        self.assertGreaterEqual(len(senior_eng['bullets']), 2)
        
        # Validate education
        self.assertGreaterEqual(len(education), 1)
        self.assertIn('stanford', education[0]['institution'].lower())
        self.assertIn('computer science', education[0]['degree'].lower())
        
        # Validate skills
        all_skills = skills['technical_skills'] + skills['soft_skills'] + skills['other_skills']
        self.assertGreaterEqual(len(all_skills), 10)
        skill_text = ' '.join(all_skills).lower()
        for expected_skill in ['python', 'javascript', 'react', 'aws']:
            self.assertIn(expected_skill.lower(), skill_text)
        
        # Validate certifications
        self.assertGreaterEqual(len(certifications), 1)
        cert_names = [cert['name'].lower() for cert in certifications]
        self.assertTrue(any('aws' in name for name in cert_names))

    def test_section_identification(self):
        """Test that all sections in the sample resume are correctly identified."""
        # Normalize the text
        normalized_text = normalize_text(self.sample_resume_text)
        
        # Identify sections
        sections = identify_sections(normalized_text)
        
        # Check that all expected sections are present
        expected_sections = [
            'summary', 'experience', 'education', 'skills', 
            'certifications', 'projects', 'languages', 'interests'
        ]
        
        for section in expected_sections:
            self.assertIn(section, sections)
            self.assertNotEqual(sections[section], '')
        
        # Check section content
        self.assertIn('5+ years', sections['summary'])
        self.assertIn('Tech Solutions', sections['experience'])
        self.assertIn('Stanford University', sections['education'])
        self.assertIn('Python', sections['skills'])
        self.assertIn('AWS Certified', sections['certifications'])
        self.assertIn('Personal Website', sections['projects'])
        self.assertIn('English', sections['languages'])
        self.assertIn('Rock climbing', sections['interests'])

if __name__ == '__main__':
    unittest.main() 