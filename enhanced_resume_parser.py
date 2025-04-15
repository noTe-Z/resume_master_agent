#!/usr/bin/env python3
"""
Enhanced Resume Parser Display Script

This script takes a resume file path as input, parses it using pdfminer directly,
and extracts structured data with focus on work experience and academic research.
"""

import os
import sys
import re
import argparse
from pprint import pprint
from pdfminer.high_level import extract_text

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description='Parse a resume and display the content section by section.')
    parser.add_argument('file_path', help='Path to the resume file (PDF, DOC, or DOCX)')
    return parser.parse_args()

def print_section_header(title):
    """Print a section header with decorative formatting."""
    print("\n" + "=" * 50)
    print(f" {title} ".center(50, "="))
    print("=" * 50)

def extract_contact_info(text):
    """Extract contact information from the resume text."""
    contact_info = {}
    
    # Extract name (assuming it's at the beginning of the resume)
    name_match = re.search(r'^(.+?)(?=\n)', text)
    if name_match:
        contact_info['name'] = name_match.group(1).strip()
    
    # Extract email
    email_match = re.search(r'[\w.+-]+@[\w-]+\.[\w.-]+', text)
    if email_match:
        contact_info['email'] = email_match.group(0)
    
    # Extract phone number
    phone_match = re.search(r'(\+\d{1,2}[-\s]?)?(\d{3}[-\s]?\d{3}[-\s]?\d{4}|\(\d{3}\)\s*\d{3}[-\s]?\d{4})', text)
    if phone_match:
        contact_info['phone'] = phone_match.group(0)
    
    # Extract LinkedIn
    linkedin_match = re.search(r'linkedin\.com/in/[\w-]+', text)
    if linkedin_match:
        contact_info['linkedin'] = linkedin_match.group(0)
    
    return contact_info

def identify_sections(text):
    """
    Identify different sections in the resume.
    Returns a dictionary with section names as keys and section text as values.
    """
    # Common section headers in resumes
    section_headers = {
        'summary': ['summary', 'professional summary', 'profile', 'about me', 'objective'],
        'experience': ['experience', 'work experience', 'employment', 'work history', 'professional experience'],
        'education': ['education', 'academic background', 'qualifications'],
        'skills': ['skills', 'technical skills', 'core skills', 'key skills'],
        'projects': ['projects', 'personal projects', 'academic projects', 'research projects', 'research experience'],
        'certifications': ['certifications', 'certificates'],
        'publications': ['publications', 'papers', 'research papers'],
        'awards': ['awards', 'honors', 'achievements'],
        'research': ['research', 'research experience', 'academic research']
    }
    
    # Convert text to lowercase for easier matching
    text_lower = text.lower()
    
    # Find the starting point of each section
    section_starts = {}
    
    for section, headers in section_headers.items():
        for header in headers:
            # Look for section headers followed by a newline or colon
            pattern = r'(^|\n)(' + re.escape(header) + r')[\s:]*(\n|$)'
            match = re.search(pattern, text_lower)
            if match:
                start_pos = match.start()
                # Store the actual matched header text from the original text
                original_header = text[match.start(2):match.end(2)]
                section_starts[section] = (start_pos, original_header)
                break
    
    # Sort sections by their starting position in the document
    sorted_sections = sorted(section_starts.items(), key=lambda x: x[1][0])
    
    # Extract each section's content
    sections = {}
    for i, (section, (start_pos, header)) in enumerate(sorted_sections):
        # Find the section end (the start of the next section)
        if i < len(sorted_sections) - 1:
            end_pos = sorted_sections[i + 1][1][0]
        else:
            end_pos = len(text)
        
        # Extract section content
        header_pos = start_pos + len(header)
        section_text = text[header_pos:end_pos].strip()
        sections[section] = section_text
    
    # Get all text before the first section as "header"
    if sorted_sections:
        first_section_start = sorted_sections[0][1][0]
        sections['header'] = text[:first_section_start].strip()
    else:
        sections['header'] = text.strip()
    
    return sections

def extract_experiences(text):
    """
    Extract work experiences from the experience section.
    Returns a list of dictionaries, each containing details about one experience.
    """
    if not text:
        return []
    
    experiences = []
    # Split text into possible experience entries based on common patterns
    entries = re.split(r'\n\s*\n', text)
    
    for entry in entries:
        if not entry.strip():
            continue
        
        experience = {}
        
        # Try to extract company and position
        company_position_match = re.search(r'^(.+?)(?:,|\n|$)(.*?)(?:\n|$)', entry.strip())
        if company_position_match:
            experience['company'] = company_position_match.group(1).strip()
            experience['position'] = company_position_match.group(2).strip()
        
        # Extract dates (format: MM/YYYY - MM/YYYY or similar)
        date_match = re.search(r'(\d{1,2}/\d{4}|\d{4})\s*[-–—]\s*(\d{1,2}/\d{4}|\d{4}|Present|Current)', entry)
        if date_match:
            experience['start_date'] = date_match.group(1)
            experience['end_date'] = date_match.group(2)
        else:
            # Just years
            date_match = re.search(r'(\d{4})\s*[-–—]\s*(\d{4}|Present|Current)', entry)
            if date_match:
                experience['start_date'] = date_match.group(1)
                experience['end_date'] = date_match.group(2)
        
        # Extract location if present
        location_match = re.search(r'([A-Z][a-z]+(?:[\s,]+[A-Z][a-z]+)*),\s*([A-Z]{2})', entry)
        if location_match:
            experience['location'] = f"{location_match.group(1)}, {location_match.group(2)}"
        
        # Extract responsibilities (bullet points or lines after company/position/dates)
        lines = entry.split('\n')
        responsibilities = []
        capture_mode = False
        
        for line in lines:
            line = line.strip()
            # Skip empty lines
            if not line:
                continue
                
            # Skip company, position, and date lines
            if (experience.get('company') and experience['company'] in line) or \
               (experience.get('position') and experience['position'] in line) or \
               (date_match and date_match.group(0) in line):
                continue
            
            # If line starts with a bullet point or dash, or previous line was a responsibility, add it
            if line.startswith('•') or line.startswith('-') or line.startswith('*') or capture_mode:
                responsibility = line.lstrip('•-* ')
                if responsibility:
                    responsibilities.append(responsibility)
                capture_mode = True
        
        experience['responsibilities'] = responsibilities
        experiences.append(experience)
    
    return experiences

def extract_research(text):
    """
    Extract academic research information.
    Returns a list of research projects/experiences.
    """
    if not text:
        return []
    
    research_items = []
    # Split text into possible research entries
    entries = re.split(r'\n\s*\n', text)
    
    for entry in entries:
        if not entry.strip():
            continue
        
        research = {}
        
        # Try to extract project title and institution
        title_match = re.search(r'^(.+?)(?:,|\n|$)', entry.strip())
        if title_match:
            research['title'] = title_match.group(1).strip()
        
        # Extract dates (format: MM/YYYY - MM/YYYY or similar)
        date_match = re.search(r'(\d{1,2}/\d{4}|\d{4})\s*[-–—]\s*(\d{1,2}/\d{4}|\d{4}|Present|Current)', entry)
        if date_match:
            research['start_date'] = date_match.group(1)
            research['end_date'] = date_match.group(2)
        else:
            # Just years
            date_match = re.search(r'(\d{4})\s*[-–—]\s*(\d{4}|Present|Current)', entry)
            if date_match:
                research['start_date'] = date_match.group(1)
                research['end_date'] = date_match.group(2)
        
        # Extract description (bullet points or lines after title/dates)
        lines = entry.split('\n')
        description = []
        capture_mode = False
        
        for line in lines:
            line = line.strip()
            # Skip empty lines
            if not line:
                continue
                
            # Skip title and date lines
            if (research.get('title') and research['title'] in line) or \
               (date_match and date_match.group(0) in line):
                continue
            
            # If line starts with a bullet point or dash, or previous line was a description, add it
            if line.startswith('•') or line.startswith('-') or line.startswith('*') or capture_mode:
                detail = line.lstrip('•-* ')
                if detail:
                    description.append(detail)
                capture_mode = True
            elif not description:  # If no description yet, this might be part of the title/institution
                if not research.get('institution'):
                    research['institution'] = line
                else:
                    description.append(line)
        
        research['description'] = description
        research_items.append(research)
    
    return research_items

def parse_resume(file_path):
    """Parse a resume file and extract structured information."""
    # Extract text from PDF
    text = extract_text(file_path)
    
    # Identify sections in the resume
    sections = identify_sections(text)
    
    # Extract contact information from the header
    contact_info = extract_contact_info(sections.get('header', '') or text[:500])
    
    # Extract experiences from the experience section
    experiences = extract_experiences(sections.get('experience', ''))
    
    # Extract research information
    research = extract_research(sections.get('research', ''))
    
    # If no research section was found, try looking in the projects section
    if not research and 'projects' in sections:
        research = extract_research(sections.get('projects', ''))
    
    # Combine all parsed data
    resume_data = {
        'contact_info': contact_info,
        'summary': sections.get('summary', ''),
        'experiences': experiences,
        'education': sections.get('education', ''),
        'skills': sections.get('skills', ''),
        'research': research,
        'raw_sections': sections
    }
    
    return resume_data

def print_contact_info(contact_info):
    """Print contact information in a readable format."""
    print_section_header("CONTACT INFORMATION")
    if not contact_info:
        print("No contact information found.")
        return
    
    for key, value in contact_info.items():
        if value:
            print(f"{key.replace('_', ' ').title()}: {value}")

def print_experiences(experiences):
    """Print work experiences in a readable format."""
    print_section_header("WORK EXPERIENCE")
    if not experiences:
        print("No work experience found.")
        return
    
    for i, exp in enumerate(experiences, 1):
        print(f"\n[Experience {i}]")
        print(f"Company: {exp.get('company', 'N/A')}")
        print(f"Position: {exp.get('position', 'N/A')}")
        if 'location' in exp:
            print(f"Location: {exp.get('location', 'N/A')}")
        print(f"Start Date: {exp.get('start_date', 'N/A')}")
        print(f"End Date: {exp.get('end_date', 'N/A')}")
        
        if 'responsibilities' in exp and exp['responsibilities']:
            print("\nResponsibilities:")
            for resp in exp['responsibilities']:
                print(f"  • {resp}")

def print_research(research):
    """Print academic research in a readable format."""
    print_section_header("ACADEMIC RESEARCH")
    if not research:
        print("No academic research found.")
        return
    
    for i, res in enumerate(research, 1):
        print(f"\n[Research {i}]")
        print(f"Title: {res.get('title', 'N/A')}")
        if 'institution' in res:
            print(f"Institution: {res.get('institution', 'N/A')}")
        print(f"Start Date: {res.get('start_date', 'N/A')}")
        print(f"End Date: {res.get('end_date', 'N/A')}")
        
        if 'description' in res and res['description']:
            print("\nDescription:")
            for desc in res['description']:
                print(f"  • {desc}")

def print_education(education_text):
    """Print education in a readable format."""
    print_section_header("EDUCATION")
    if not education_text:
        print("No education found.")
        return
    
    print(education_text)

def print_skills(skills_text):
    """Print skills in a readable format."""
    print_section_header("SKILLS")
    if not skills_text:
        print("No skills found.")
        return
    
    print(skills_text)

def print_raw_text(text, section_name):
    """Print raw text of a section."""
    print_section_header(f"RAW {section_name.upper()}")
    print(text)

def main():
    """Main entry point for the script."""
    args = parse_args()
    
    try:
        # Check if file exists
        if not os.path.exists(args.file_path):
            print(f"Error: File not found: {args.file_path}")
            sys.exit(1)
        
        # Parse resume
        print(f"Parsing resume: {args.file_path}")
        resume_data = parse_resume(args.file_path)
        
        # Print sections
        print_contact_info(resume_data.get('contact_info', {}))
        
        # Print experiences
        print_experiences(resume_data.get('experiences', []))
        
        # Print research
        print_research(resume_data.get('research', []))
        
        # Print education and skills as raw text
        print_education(resume_data.get('education', ''))
        print_skills(resume_data.get('skills', ''))
        
        # Print raw sections for debugging
        for section_name, section_text in resume_data.get('raw_sections', {}).items():
            if section_name not in ['header', 'education', 'skills'] and section_text:
                print_raw_text(section_text, section_name)
        
        print("\nResume parsing completed successfully!")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 