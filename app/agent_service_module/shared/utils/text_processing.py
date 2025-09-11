"""
Text processing utilities for content analysis and manipulation
"""

import re
from typing import List, Dict, Any, Optional
from datetime import datetime


class TextProcessor:
    """Text processing utility class"""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text content"""
        return clean_text(text)
    
    @staticmethod
    def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
        """Extract keywords from text content"""
        return extract_keywords(text, max_keywords)
    
    @staticmethod
    def calculate_readability_score(text: str) -> float:
        """Calculate a simple readability score (0-1)"""
        return calculate_readability_score(text)
    
    @staticmethod
    def summarize_text(text: str, max_length: int = 500) -> str:
        """Create a summary of text content"""
        return summarize_text(text, max_length)
    
    @staticmethod
    def detect_language(text: str) -> str:
        """Simple language detection"""
        return detect_language(text)
    
    @staticmethod
    def calculate_content_quality_score(content: Dict[str, Any]) -> float:
        """Calculate overall content quality score"""
        return calculate_content_quality_score(content)


def clean_text(text: str) -> str:
    """Clean and normalize text content"""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s\.\,\!\?\-\(\)]', '', text)
    
    return text


def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """Extract keywords from text content"""
    if not text:
        return []
    
    # Simple keyword extraction - split by common separators
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    
    # Remove common stop words
    stop_words = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'man', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'its', 'let', 'put', 'say', 'she', 'too', 'use'}
    
    keywords = [word for word in words if word not in stop_words]
    
    # Count frequency and return most common
    word_count = {}
    for word in keywords:
        word_count[word] = word_count.get(word, 0) + 1
    
    # Sort by frequency and return top keywords
    sorted_keywords = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
    return [word for word, count in sorted_keywords[:max_keywords]]


def calculate_readability_score(text: str) -> float:
    """Calculate a simple readability score (0-1)"""
    if not text:
        return 0.0
    
    words = len(text.split())
    sentences = len(re.findall(r'[.!?]+', text))
    
    if sentences == 0:
        return 0.5  # Default score for text without sentences
    
    avg_words_per_sentence = words / sentences
    
    # Simple scoring: prefer 10-20 words per sentence
    if 10 <= avg_words_per_sentence <= 20:
        score = 1.0
    elif avg_words_per_sentence < 10:
        score = avg_words_per_sentence / 10
    else:
        score = max(0.1, 1.0 - (avg_words_per_sentence - 20) / 50)
    
    return min(1.0, max(0.0, score))


def extract_dates_from_text(text: str) -> List[str]:
    """Extract date patterns from text"""
    if not text:
        return []
    
    date_patterns = [
        r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
        r'\d{1,2}/\d{1,2}/\d{4}',  # MM/DD/YYYY
        r'\d{1,2}-\d{1,2}-\d{4}',  # MM-DD-YYYY
        r'[A-Za-z]+ \d{1,2}, \d{4}',  # Month DD, YYYY
    ]
    
    dates = []
    for pattern in date_patterns:
        matches = re.findall(pattern, text)
        dates.extend(matches)
    
    return dates


def summarize_text(text: str, max_length: int = 500) -> str:
    """Create a summary of text content"""
    if not text:
        return ""
    
    if len(text) <= max_length:
        return text
    
    # Simple summarization: take first few sentences up to max_length
    sentences = re.split(r'[.!?]+', text)
    summary = ""
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        if len(summary + sentence) <= max_length - 3:  # Leave room for "..."
            summary += sentence + ". "
        else:
            break
    
    if len(summary) < len(text):
        summary = summary.rstrip() + "..."
    
    return summary.strip()


def detect_language(text: str) -> str:
    """Simple language detection (returns 'en' for now)"""
    # Placeholder implementation - always returns English
    # In a real implementation, you might use langdetect or similar
    return "en"


def calculate_content_quality_score(content: Dict[str, Any]) -> float:
    """Calculate overall content quality score"""
    score = 0.0
    
    # Title quality (20%)
    title = content.get('title', '')
    if title and len(title) > 10:
        score += 0.2
    
    # Content length (30%)
    text = content.get('content', '')
    word_count = len(text.split()) if text else 0
    if word_count >= 100:
        score += 0.3
    elif word_count >= 50:
        score += 0.15
    
    # Readability (20%)
    if text:
        readability = calculate_readability_score(text)
        score += readability * 0.2
    
    # Metadata presence (15%)
    if content.get('author'):
        score += 0.075
    if content.get('published_date'):
        score += 0.075
    
    # URL quality (15%)
    url = content.get('url', '')
    if url and any(domain in url for domain in ['gov', 'edu', 'org']):
        score += 0.15
    elif url:
        score += 0.075
    
    return min(1.0, score)


def parse_s3_uri(s3_uri: str) -> str:
    """
    Parse S3 URI and extract the object key.
    
    Args:
        s3_uri: S3 URI in format s3://bucket/path/to/object or just path/to/object
        
    Returns:
        str: The object key (path without s3://bucket/ prefix)
        
    Examples:
        parse_s3_uri("s3://bucket/summaries/req_123/summary.json") -> "summaries/req_123/summary.json"
        parse_s3_uri("summaries/req_123/summary.json") -> "summaries/req_123/summary.json"
    """
    if not s3_uri:
        return ""
    
    # If it's already just an object key (no s3:// prefix), return as is
    if not s3_uri.startswith('s3://'):
        return s3_uri
    
    # Parse s3://bucket/path/to/object
    # Remove s3:// prefix
    uri_without_protocol = s3_uri[5:]  # Remove 's3://'
    
    # Find first slash after bucket name
    first_slash_index = uri_without_protocol.find('/')
    if first_slash_index == -1:
        # No path after bucket name
        return ""
    
    # Return everything after bucket/
    object_key = uri_without_protocol[first_slash_index + 1:]
    return object_key 