
=============================================================================

MODULES/EMAIL_HARVESTER.PY - EMAIL HARVESTER

=============================================================================

import csv
import time
import random
import requests
from datetime import datetime
from typing import List, Dict, Any, Set
from bs4 import BeautifulSoup
from pathlib import Path
import re
from urllib.parse import urljoin, urlparse

class EmailHarvester:
"""Email harvester for venue websites"""

def __init__(self, config: Dict[str, Any]):  
    self.config = config  
    self.harvester_config = config.get('email_harvester', {})  
    self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')  
    self.user_agents = self.harvester_config.get('user_agents', [  
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',  
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',  
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'  
    ])  
    self.timeout = self.harvester_config.get('timeout', 15)  
    self.delay_min = self.harvester_config.get('delay_min', 5)  
    self.delay_max = self.harvester_config.get('delay_max', 15)  
    self.pages_to_check = self.harvester_config.get('pages_to_check', [  
        '', '/contact', '/about', '/contact-us', '/about-us', '/info'  
    ])  
    self.session = requests.Session()  
      
def harvest_emails(self) -> Dict[str, Any]:  
    """Harvest emails from all venue websites"""  
    venues = self._load_venues()  
    results = []  
      
    for i, venue_data in enumerate(venues):  
        venue_name = venue_data.get('venue_name', 'Unknown')  
        website = venue_data.get('website', '')  
          
        if not website:  
            continue  
          
        # Add random delay  
        if i > 0:  
            delay = random.randint(self.delay_min, self.delay_max)  
            time.sleep(delay)  
          
        emails = self._harvest_website_emails(website, venue_name)  
          
        if emails:  
            result = {  
                'venue_name': venue_name,  
                'website': website,  
                'emails': list(emails),  
                'email_count': len(emails),  
                'status': 'success',  
                'timestamp': datetime.now().isoformat()  
            }  
        else:  
            result = {  
                'venue_name': venue_name,  
                'website': website,  
                'emails': [],  
                'email_count': 0,  
                'status': 'no_emails_found',  
                'timestamp': datetime.now().isoformat()  
            }  
          
        results.append(result)  
        self._log_harvest_result(result)  
      
    # Save results  
    self._save_harvest_results(results)  
      
    return {  
        'total_websites_checked': len(results),  
        'websites_with_emails': len([r for r in results if r['email_count'] > 0]),  
        'total_emails_found': sum(r['email_count'] for r in results),  
        'results': results  
    }  
  
def _harvest_website_emails(self, website: str, venue_name: str) -> Set[str]:  
    """Harvest emails from a single website"""  
    emails = set()  
      
    # Ensure website has protocol  
    if not website.startswith(('http://', 'https://')):  
        website = f'https://{website}'  
      
    # Try different pages  
    for page_path in self.pages_to_check:  
        try:  
            url = urljoin(website, page_path)  
            page_emails = self._extract_emails_from_page(url)  
            emails.update(page_emails)  
              
            # Small delay between page requests  
            time.sleep(1)  
              
        except Exception as e:  
            continue  
      
    # Filter out common false positives  
    filtered_emails = self._filter_emails(emails)  
      
    return filtered_emails  
  
def _extract_emails_from_page(self, url: str) -> Set[str]:  
    """Extract emails from a single page"""  
    emails = set()  
      
    try:  
        headers = {  
            'User-Agent': random.choice(self.user_agents),  
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',  
            'Accept-Language': 'en-US,en;q=0.5',  
            'Accept-Encoding': 'gzip, deflate',  
            'Connection': 'keep-alive',  
        }  
          
        response = self.session.get(url, headers=headers, timeout=self.timeout)  
        response.raise_for_status()  
          
        # Extract emails from HTML content  
        soup = BeautifulSoup(response.content, 'html.parser')  
          
        # Remove script and style elements  
        for script in soup(["script", "style"]):  
            script.decompose()  
          
        # Get text content  
        text = soup.get_text()  
          
        # Find emails using regex  
        found_emails = self.email_pattern.findall(text)  
        emails.update(found_emails)  
          
        # Also check href attributes for mailto links  
        for link in soup.find_all('a', href=True):  
            href = link['href']  
            if href.startswith('mailto:'):  
                email = href.replace('mailto:', '').split('?')[0]  
                if self.email_pattern.match(email):  
                    emails.add(email)  
          
    except Exception as e:  
        pass  
      
    return emails  
  
def _filter_emails(self, emails: Set[str]) -> Set[str]:  
    """Filter out common false positives and invalid emails"""  
    filtered = set()  
      
    # Common false positives to exclude  
    exclude_patterns = [  
        r'.*@example\.com,  
        r'.*@domain\.com,  
        r'.*@yoursite\.com,  
        r'.*@sentry\.io,  
        r'.*@google\.com,  
        r'.*@facebook\.com,  
        r'.*@twitter\.com,  
        r'.*@instagram\.com,  
        r'.*@linkedin\.com,  
        r'.*@youtube\.com,  
        r'.*@wordpress\.com,  
        r'.*@wix\.com,  
        r'.*@squarespace\.com,  
    ]  
      
    for email in emails:  
        email = email.lower().strip()  
          
        # Skip if matches exclude patterns  
        if any(re.match(pattern, email) for pattern in exclude_patterns):  
            continue  
          
        # Skip if too short or too long  
        if len(email) < 5 or len(email) > 100:  
            continue  
          
        # Skip if contains suspicious characters  
        if any(char in email for char in ['<', '>', '"', "'"]):  
            continue  
          
        filtered.add(email)  
      
    return filtered  
  
def _load_venues(self) -> List[Dict[str, str]]:  
    """Load venues from CSV"""  
    venues_file = Path('data/venues.csv')  
    if not venues_file.exists():  
        return []  
      
    with open(venues_file, 'r', encoding='utf-8') as f:  
        return list(csv.DictReader(f))  
  
def _log_harvest_result(self, result: Dict[str, Any]):  
    """Log individual harvest result"""  
    venue = result['venue_name']  
    email_count = result['email_count']  
      
    if email_count > 0:  
        print(f"✓ Found {email_count} emails for {venue}")  
    else:  
        print(f"✗ No emails found for {venue}")  
  
def _save_harvest_results(self, results: List[Dict[str, Any]]):  
    """Save harvest results to CSV"""  
    results_dir = Path('data/results')  
    results_dir.mkdir(exist_ok=True)  
      
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')  
    results_file = results_dir / f'email_harvest_{timestamp}.csv'  
      
    # Flatten results for CSV  
    flattened_results = []  
    for result in results:  
        if result['emails']:  
            for email in result['emails']:  
                flattened_results.append({  
                    'venue_name': result['venue_name'],  
                    'website': result['website'],  
                    'email': email,  
                    'timestamp': result['timestamp']  
                })  
        else:  
            flattened_results.append({  
                'venue_name': result['venue_name'],  
                'website': result['website'],  
                'email': '',  
                'timestamp': result['timestamp']  
            })  
      
    if flattened_results:  
        fieldnames = ['venue_name', 'website', 'email', 'timestamp']  
        with open(results_file, 'w', newline='', encoding='utf-8') as f:  
            writer = csv.DictWriter(f, fieldnames=fieldnames)  
            writer.writeheader()  
            writer.writerows(flattened_results)
