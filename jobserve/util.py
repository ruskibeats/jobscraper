"""
Utility functions for the JobServe scraper.
"""

import re
from datetime import datetime, timedelta
from typing import Optional, Tuple

from .constant import JOB_TYPE_MAPPINGS, CURRENCY_MAPPINGS

def parse_job_type(job_type_text: str) -> Optional[str]:
    """
    Parse job type from text.
    
    Args:
        job_type_text: The job type text to parse.
        
    Returns:
        The parsed job type, or None if not found.
    """
    if not job_type_text:
        return None
        
    job_type_text = job_type_text.lower()
    
    # Check for direct matches in the mappings
    for key, value in JOB_TYPE_MAPPINGS.items():
        if key in job_type_text:
            return value
    
    return None

def parse_date_posted(date_text: str) -> Optional[datetime]:
    """
    Parse date posted from text.
    
    Args:
        date_text: The date text to parse.
        
    Returns:
        The parsed date, or None if not found.
    """
    if not date_text:
        return None
        
    date_text = date_text.lower()
    today = datetime.now()
    
    # Check for "X days ago"
    days_ago_match = re.search(r'(\d+)\s+days?\s+ago', date_text)
    if days_ago_match:
        days = int(days_ago_match.group(1))
        return today - timedelta(days=days)
    
    # Check for "X hours ago"
    hours_ago_match = re.search(r'(\d+)\s+hours?\s+ago', date_text)
    if hours_ago_match:
        hours = int(hours_ago_match.group(1))
        return today - timedelta(hours=hours)
    
    # Check for "today"
    if 'today' in date_text:
        return today
    
    # Check for "yesterday"
    if 'yesterday' in date_text:
        return today - timedelta(days=1)
    
    # Check for specific date format (e.g., "Jan 1, 2023")
    try:
        return datetime.strptime(date_text, '%b %d, %Y')
    except ValueError:
        pass
    
    # Check for specific date format (e.g., "01/01/2023")
    try:
        return datetime.strptime(date_text, '%d/%m/%Y')
    except ValueError:
        pass
    
    # Check for specific date format (e.g., "2023-01-01")
    try:
        return datetime.strptime(date_text, '%Y-%m-%d')
    except ValueError:
        pass
    
    return None

def parse_salary(salary_text: str) -> Tuple[Optional[str], Optional[float], Optional[float], Optional[str]]:
    """
    Parse salary information from text.
    
    Args:
        salary_text: The salary text to parse.
        
    Returns:
        A tuple of (interval, min_amount, max_amount, currency).
    """
    if not salary_text:
        return None, None, None, None
        
    salary_text = salary_text.lower()
    
    # Initialize return values
    interval = None
    min_amount = None
    max_amount = None
    currency = "GBP"  # Default to GBP for JobServe UK
    
    # Check for currency
    for symbol, code in CURRENCY_MAPPINGS.items():
        if symbol.lower() in salary_text:
            currency = code
            break
    
    # Check for interval
    if any(term in salary_text for term in ['per year', '/year', 'yearly', 'per annum', 'p.a.', 'annual']):
        interval = "yearly"
    elif any(term in salary_text for term in ['per month', '/month', 'monthly', 'pcm']):
        interval = "monthly"
    elif any(term in salary_text for term in ['per week', '/week', 'weekly']):
        interval = "weekly"
    elif any(term in salary_text for term in ['per day', '/day', 'daily', 'pd']):
        interval = "daily"
    elif any(term in salary_text for term in ['per hour', '/hour', 'hourly', 'ph']):
        interval = "hourly"
    else:
        # Default to yearly if no interval is specified but there's a number
        if re.search(r'\d', salary_text):
            interval = "yearly"
    
    # Extract salary range with currency symbols
    range_match = re.search(r'([£$€¥₹])?(\d[\d,]*\.?\d*)\s*-\s*([£$€¥₹])?(\d[\d,]*\.?\d*)', salary_text)
    if range_match:
        min_currency = range_match.group(1)
        min_amount = float(range_match.group(2).replace(',', ''))
        max_currency = range_match.group(3)
        max_amount = float(range_match.group(4).replace(',', ''))
        
        # Use the currency from the match if available
        if min_currency and min_currency.lower() in CURRENCY_MAPPINGS:
            currency = CURRENCY_MAPPINGS[min_currency.lower()]
        elif max_currency and max_currency.lower() in CURRENCY_MAPPINGS:
            currency = CURRENCY_MAPPINGS[max_currency.lower()]
    else:
        # Extract single salary with currency symbol
        single_match = re.search(r'([£$€¥₹])?(\d[\d,]*\.?\d*)', salary_text)
        if single_match:
            found_currency = single_match.group(1)
            amount = float(single_match.group(2).replace(',', ''))
            min_amount = amount
            max_amount = amount
            
            # Use the currency from the match if available
            if found_currency and found_currency.lower() in CURRENCY_MAPPINGS:
                currency = CURRENCY_MAPPINGS[found_currency.lower()]
    
    return interval, min_amount, max_amount, currency

def is_remote_job(job_text: str) -> bool:
    """
    Check if a job is remote based on its description.
    
    Args:
        job_text: The job text to check.
        
    Returns:
        True if the job is remote, False otherwise.
    """
    if not job_text:
        return False
        
    job_text = job_text.lower()
    remote_keywords = [
        'remote', 
        'work from home', 
        'wfh', 
        'telecommute', 
        'virtual', 
        'home based', 
        'home-based',
        'remote working',
        'remote work',
        'working remotely',
        'work remotely'
    ]
    
    for keyword in remote_keywords:
        if keyword in job_text:
            return True
    
    return False

def extract_emails(text: str) -> list[str]:
    """
    Extract email addresses from text.
    
    Args:
        text: The text to extract emails from.
        
    Returns:
        A list of email addresses.
    """
    if not text:
        return []
        
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    return re.findall(email_pattern, text)
