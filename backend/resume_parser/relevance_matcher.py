#!/usr/bin/env python3
"""
Resume Relevance Matcher Module

This module provides functions for matching resume content against job descriptions
to determine relevance scores and optimize content selection.
"""

import re
import math
from typing import Dict, List, Any, Optional, Tuple
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Download required NLTK resources
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')

# Initialize NLTK components
stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

def preprocess_text(text: str) -> List[str]:
    """
    Preprocess text for NLP analysis.
    
    Args:
        text: Raw text string
        
    Returns:
        List of preprocessed tokens
    """
    # Convert to lowercase
    text = text.lower()
    
    # Remove punctuation and numbers
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\d+', ' ', text)
    
    # Tokenize
    tokens = word_tokenize(text)
    
    # Remove stopwords and lemmatize
    tokens = [lemmatizer.lemmatize(token) for token in tokens if token not in stop_words]
    
    return tokens

def extract_keywords(text: str, top_n: int = 30) -> List[str]:
    """
    Extract the most important keywords from text.
    
    Args:
        text: Raw text string
        top_n: Number of top keywords to return
        
    Returns:
        List of important keywords
    """
    # Preprocess text
    tokens = preprocess_text(text)
    
    # Count token frequencies
    token_freq = {}
    for token in tokens:
        if len(token) > 2:  # Only consider tokens longer than 2 characters
            token_freq[token] = token_freq.get(token, 0) + 1
    
    # Sort by frequency
    sorted_tokens = sorted(token_freq.items(), key=lambda x: x[1], reverse=True)
    
    # Return top N keywords
    return [token for token, _ in sorted_tokens[:top_n]]

def calculate_tfidf(doc_tokens: List[str], all_docs_tokens: List[List[str]]) -> Dict[str, float]:
    """
    Calculate TF-IDF scores for tokens in a document.
    
    Args:
        doc_tokens: Tokens from the target document
        all_docs_tokens: List of token lists from all documents
        
    Returns:
        Dictionary mapping tokens to their TF-IDF scores
    """
    # Calculate term frequency
    tf = {}
    for token in doc_tokens:
        tf[token] = tf.get(token, 0) + 1
    
    # Normalize term frequency by document length
    for token in tf:
        tf[token] = tf[token] / len(doc_tokens)
    
    # Calculate inverse document frequency
    idf = {}
    num_docs = len(all_docs_tokens)
    
    for token in set(doc_tokens):
        # Count documents containing this token
        doc_count = sum(1 for doc in all_docs_tokens if token in doc)
        idf[token] = math.log(num_docs / (1 + doc_count))
    
    # Calculate TF-IDF
    tfidf = {}
    for token in doc_tokens:
        tfidf[token] = tf[token] * idf.get(token, 0)
    
    return tfidf

def score_experience_relevance(experience: Dict[str, Any], job_description: str) -> float:
    """
    Score the relevance of a resume experience item against a job description.
    
    Args:
        experience: Dictionary containing experience details
        job_description: Job description text
        
    Returns:
        Relevance score (0.0 to 1.0)
    """
    # Extract experience text
    exp_text = ""
    if 'title' in experience:
        exp_text += experience['title'] + " "
    if 'position' in experience:
        exp_text += experience['position'] + " "
    if 'company' in experience:
        exp_text += experience['company'] + " "
    if 'description' in experience:
        exp_text += experience['description'] + " "
    
    # Add responsibilities
    if 'responsibilities' in experience and experience['responsibilities']:
        if isinstance(experience['responsibilities'], list):
            exp_text += " ".join(experience['responsibilities'])
        else:
            exp_text += str(experience['responsibilities'])
            
    # Add bullets
    if 'bullets' in experience and experience['bullets']:
        exp_text += " ".join(experience['bullets'])
    
    # Preprocess text
    job_tokens = preprocess_text(job_description)
    exp_tokens = preprocess_text(exp_text)
    
    # Calculate TF-IDF for job description
    job_tfidf = calculate_tfidf(job_tokens, [exp_tokens, job_tokens])
    
    # Get top job description keywords by TF-IDF score
    top_job_keywords = sorted(job_tfidf.items(), key=lambda x: x[1], reverse=True)[:50]
    top_job_keywords = [k for k, _ in top_job_keywords]
    
    # Calculate match score based on keyword matches
    matches = sum(1 for token in exp_tokens if token in top_job_keywords)
    coverage = matches / len(top_job_keywords) if top_job_keywords else 0
    
    # Normalize to 0-1 range
    score = min(1.0, coverage * 2)  # Scale up to make higher scores more attainable
    
    return score

def rank_experiences(experiences: List[Dict[str, Any]], job_description: str) -> List[Dict[str, Any]]:
    """
    Rank resume experiences by relevance to job description.
    
    Args:
        experiences: List of experience dictionaries
        job_description: Job description text
        
    Returns:
        List of experiences with relevance scores, sorted by relevance
    """
    scored_experiences = []
    
    for exp in experiences:
        score = score_experience_relevance(exp, job_description)
        scored_exp = exp.copy()
        scored_exp['relevance_score'] = score
        scored_experiences.append(scored_exp)
    
    # Sort by relevance score (descending)
    sorted_experiences = sorted(scored_experiences, key=lambda x: x.get('relevance_score', 0), reverse=True)
    
    return sorted_experiences

def select_relevant_experiences(experiences: List[Dict[str, Any]], job_description: str, max_items: int = 3) -> List[Dict[str, Any]]:
    """
    Select the most relevant experiences for a job description.
    
    Args:
        experiences: List of experience dictionaries
        job_description: Job description text
        max_items: Maximum number of experiences to select
        
    Returns:
        List of most relevant experiences
    """
    # Rank experiences by relevance
    ranked_experiences = rank_experiences(experiences, job_description)
    
    # Select top experiences (up to max_items)
    selected_experiences = ranked_experiences[:max_items]
    
    # Require minimum relevance score to be included
    selected_experiences = [exp for exp in selected_experiences if exp.get('relevance_score', 0) >= 0.2]
    
    return selected_experiences

def identify_skill_gaps(resume_skills: List[str], job_description: str) -> List[str]:
    """
    Identify skills mentioned in the job description but not in the resume.
    
    Args:
        resume_skills: List of skills from the resume
        job_description: Job description text
        
    Returns:
        List of potential skill gaps
    """
    # Extract job skills
    job_tokens = preprocess_text(job_description)
    all_tokens = [job_tokens, preprocess_text(" ".join(resume_skills))]
    
    # Calculate TF-IDF for job tokens
    job_tfidf = calculate_tfidf(job_tokens, all_tokens)
    
    # Get top job skill keywords
    top_job_skills = sorted(job_tfidf.items(), key=lambda x: x[1], reverse=True)[:30]
    top_job_skills = [k for k, _ in top_job_skills if len(k) > 2]
    
    # Normalize resume skills for comparison
    norm_resume_skills = [s.lower() for s in resume_skills]
    norm_resume_tokens = set(preprocess_text(" ".join(norm_resume_skills)))
    
    # Find skills in job description not in resume
    gaps = [skill for skill in top_job_skills 
            if skill not in norm_resume_tokens 
            and not any(skill in s.lower() for s in resume_skills)]
    
    return gaps 