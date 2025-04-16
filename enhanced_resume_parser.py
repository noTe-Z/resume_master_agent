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
            # More flexible pattern matching to handle different styles of headers
            pattern = r'(^|\n)(' + re.escape(header) + r')s?[\s:]*(\n|$)'
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                start_pos = match.start()
                # Get the full line containing the header from the original text
                header_line_start = text.rfind('\n', 0, match.start()) + 1 if text.rfind('\n', 0, match.start()) >= 0 else 0
                header_line_end = text.find('\n', match.end())
                if header_line_end == -1:
                    header_line_end = len(text)
                original_header = text[header_line_start:header_line_end].strip()
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
        
        # Extract section content, starting from after the header
        header_pos = text.find(header, start_pos) + len(header)
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
    
    # Clean up the text to handle PDF formatting quirks
    text = re.sub(r'\n{3,}', '\n\n', text)  # Replace multiple newlines with double newline
    
    # Try to identify each job entry (company + position often appear together)
    # Split text by double newlines or patterns like "2018 - 2022" which indicate date ranges
    entries = re.split(r'\n\s*\n|(\d{4}\s*[-–—]\s*(?:\d{4}|Present|Current))', text)
    entries = [e for e in entries if e and e.strip()]  # Remove empty entries
    
    # If we have at least a company name and some details
    if len(entries) >= 2:
        experience = {}
        current_field = 'company'  # Start with company field
        
        for i, entry in enumerate(entries):
            entry = entry.strip()
            
            # Skip empty entries
            if not entry:
                continue
            
            # Date range - indicates the transition from company/position to responsibilities
            if re.match(r'\d{4}\s*[-–—]\s*(?:\d{4}|Present|Current)', entry):
                # Parse date range
                date_parts = re.search(r'(\d{4})\s*[-–—]\s*(\d{4}|Present|Current)', entry)
                if date_parts:
                    experience['start_date'] = date_parts.group(1)
                    experience['end_date'] = date_parts.group(2)
                current_field = 'responsibilities'
                # Start collecting responsibilities
                experience['responsibilities'] = []
                
            # Company and position often appear in the first entry
            elif current_field == 'company':
                # Try to extract company and position (usually separated by comma or newline)
                company_position = re.split(r',|\n', entry, 1)
                if len(company_position) > 1:
                    experience['company'] = company_position[0].strip()
                    experience['position'] = company_position[1].strip()
                else:
                    experience['company'] = entry
                    experience['position'] = ""
                
                # If this is the last entry, we need to add the experience
                if i == len(entries) - 1:
                    experiences.append(experience)
                
            # Responsibilities are usually bullet points or separate lines
            elif current_field == 'responsibilities':
                # Check if this is a bullet point or a new line
                if entry.startswith('-') or entry.startswith('•') or entry.startswith('*'):
                    responsibility = entry.lstrip('-•* ').strip()
                    experience['responsibilities'].append(responsibility)
                else:
                    # Multiple responsibilities might be separated by newlines
                    items = [item.strip() for item in entry.split('\n') if item.strip()]
                    for item in items:
                        # If it looks like a bullet point
                        if item.startswith('-') or item.startswith('•') or item.startswith('*'):
                            responsibility = item.lstrip('-•* ').strip()
                        else:
                            responsibility = item
                        experience['responsibilities'].append(responsibility)
                
                # If this is the last entry or the next entry looks like a new company
                if i == len(entries) - 1:
                    experiences.append(experience)
                    experience = {}
                    current_field = 'company'
    
    # If the above approach didn't work, try a simpler approach
    if not experiences:
        # Remove excess spacing
        text = re.sub(r'\n\s*\n', '\n\n', text)
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        current_experience = None
        
        for line in lines:
            # If line contains company/position pattern (usually has comma or colon)
            if re.search(r'[A-Z][a-zA-Z]+.*[,:].*[A-Z][a-zA-Z]+', line) and not current_experience:
                current_experience = {'company': '', 'position': '', 'responsibilities': []}
                parts = line.split(',', 1)
                if len(parts) > 1:
                    current_experience['company'] = parts[0].strip()
                    current_experience['position'] = parts[1].strip()
                else:
                    current_experience['company'] = line
            
            # If line contains a date range (YYYY - YYYY)
            elif re.search(r'\d{4}\s*[-–—]\s*(?:\d{4}|Present|Current)', line) and current_experience:
                date_match = re.search(r'(\d{4})\s*[-–—]\s*(\d{4}|Present|Current)', line)
                if date_match:
                    current_experience['start_date'] = date_match.group(1)
                    current_experience['end_date'] = date_match.group(2)
            
            # If line starts with a bullet point, it's likely a responsibility
            elif (line.startswith('-') or line.startswith('•') or line.startswith('*')) and current_experience:
                responsibility = line.lstrip('-•* ').strip()
                current_experience['responsibilities'].append(responsibility)
            
            # If we see what looks like a new company name, save the current experience and start a new one
            elif re.match(r'^[A-Z][a-zA-Z\s&]+$', line) and current_experience and current_experience.get('company'):
                experiences.append(current_experience)
                current_experience = {'company': line, 'position': '', 'responsibilities': []}
        
        # Don't forget to add the last experience
        if current_experience and current_experience.get('company'):
            experiences.append(current_experience)
    
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
    try:
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
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error in enhanced resume parser: {str(e)}")
        return {'error': str(e)}

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
    try:
        args = parse_args()
        
        # Check if file exists
        if not os.path.exists(args.file_path):
            print(f"Error: File not found: {args.file_path}")
            sys.exit(1)
        
        # Parse resume
        print(f"Parsing resume: {args.file_path}")
        resume_data = parse_resume(args.file_path)
        
        # Check for parsing errors
        if 'error' in resume_data:
            print(f"Error parsing resume: {resume_data['error']}")
            sys.exit(1)
        
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
        
        return resume_data
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 