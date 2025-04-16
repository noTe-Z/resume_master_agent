#!/usr/bin/env python3
"""
Resume Parser Package

This package provides tools for parsing and extracting structured data from resumes.
"""

from resume_parser.interface import parse_resume, save_parsed_resume, load_parsed_resume
from resume_parser.enhanced_parser import parse_resume as enhanced_parse_resume
from resume_parser.relevance_matcher import (
    score_experience_relevance,
    rank_experiences,
    select_relevant_experiences,
    identify_skill_gaps
)

__all__ = [
    'parse_resume',
    'save_parsed_resume',
    'load_parsed_resume',
    'enhanced_parse_resume',
    'score_experience_relevance',
    'rank_experiences',
    'select_relevant_experiences',
    'identify_skill_gaps'
] 