from fpdf import FPDF
import os

# Create instance of FPDF class
pdf = FPDF()

# Add a page
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
pdf.multi_cell(0, 8, 'Experienced software engineer with expertise in web development. Skilled in JavaScript, React, Node.js, and Python with a strong background in building responsive web applications.')
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
pdf.cell(0, 8, '- Developed web applications using React and Redux', ln=True)
pdf.cell(0, 8, '- Implemented RESTful APIs with Node.js and Express', ln=True)
pdf.cell(0, 8, '- Collaborated with UX designers to implement responsive designs', ln=True)
pdf.ln(5)

# Second job
pdf.set_font('Arial', 'B', 12)
pdf.cell(0, 8, 'XYZ Startup, Junior Developer', ln=True)
pdf.set_font('Arial', 'I', 10)
pdf.cell(0, 8, 'June 2016 - December 2017', ln=True)
pdf.set_font('Arial', '', 12)
pdf.cell(0, 8, '- Built and maintained company website using HTML, CSS, and jQuery', ln=True)
pdf.cell(0, 8, '- Assisted in developing internal tools for data analysis', ln=True)
pdf.ln(5)

# EDUCATION section
pdf.set_font('Arial', 'B', 14)
pdf.cell(0, 10, 'EDUCATION', ln=True)
pdf.set_font('Arial', 'B', 12)
pdf.cell(0, 8, 'University of Example, BS Computer Science', ln=True)
pdf.set_font('Arial', 'I', 10)
pdf.cell(0, 8, '2014 - 2018', ln=True)
pdf.set_font('Arial', '', 12)
pdf.cell(0, 8, '- GPA: 3.85/4.0', ln=True)
pdf.cell(0, 8, '- Dean\'s List: All semesters', ln=True)
pdf.ln(5)

# SKILLS section
pdf.set_font('Arial', 'B', 14)
pdf.cell(0, 10, 'SKILLS', ln=True)
pdf.set_font('Arial', '', 12)
pdf.multi_cell(0, 8, 'JavaScript, React, Redux, Node.js, Express, Python, Django, SQL, MongoDB, HTML, CSS, Git, AWS, Docker')

# Ensure the directory exists
os.makedirs('example_resumes', exist_ok=True)

# Save the pdf file
output_path = os.path.join('example_resumes', 'test_resume.pdf')
pdf.output(output_path)

print(f"Created test resume at {output_path}") 