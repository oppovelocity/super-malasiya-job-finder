# =============================================================================
# MODULES/SOCIAL_SCRAPER.PY - SOCIAL MEDIA SCRAPER
# =============================================================================

import csv
import time
import random
import requests
from datetime import datetime
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from pathlib import Path
import re

class SocialScraper:
    """Social media scraper for job postings and hiring content"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.scraper_config = config.get('social_scraper', {})
        self.hiring_keywords = self.scraper_config.get('hiring_keywords', [
            'hiring', 'job', 'vacancy', 'staff', 'team', 'position', 'career',
            'recruit', 'apply', 'join', 'opening', 'opportunity', 'wanted'
        ])
        self.user_agents = self.scraper_config.get('user_agents', [
            'Mozilla/5.0 (Android 10; Mobile; rv:81.0) Gecko/81.0 Firefox/81.0',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15',
            'Mozilla/5.0 (Android 11; Mobile; rv:68.0) Gecko/68.0 Firefox/88.0'
        ])
        self.delay_min = self.scraper_config.get('delay_min', 10)
        self.delay_max = self.scraper_config.get('delay_max', 30)
        self.session = requests.Session()
        
    def scrape_venues(self) -> Dict[str, Any]:
        """Scrape social media for all venues"""
        venues = self._load_venues()
        results = []
        
        for i, venue_data in enumerate(venues):
            venue_name = venue_data.get('venue_name', 'Unknown')
            facebook_url = venue_data.get('facebook_url', '')
            instagram_url = venue_data.get('instagram_url', '')
            
            # Add random delay
            if i > 0:
                delay = random.randint(self.delay_min, self.delay_max)
                time.sleep(delay)
            
            # Scrape Facebook
            if facebook_url:
                fb_result = self._scrape_facebook_page(facebook_url, venue_name)
                if fb_result:
                    results.extend(fb_result)
            
            # Scrape Instagram
            if instagram_url:
                ig_result = self._scrape_instagram_page(instagram_url, venue_name)
                if ig_result:
                    results.extend(ig_result)
        
        # Save results
        self._save_scraping_results(results)
        
        return {
            'total_venues_scraped': len(venues),
            'total_posts_found': len(results),
            'hiring_posts': len([r for r in results if r['has_hiring_keywords']]),
            'results': results
        }
    
    def _scrape_facebook_page(self, url: str, venue_name: str) -> List[Dict[str, Any]]:
        """Scrape Facebook page for job-related posts"""
        try:
            # Use mobile version for better scraping
            mobile_url = url.replace('www.facebook.com', 'm.facebook.com')
            
            headers = {
                'User-Agent': random.choice(self.user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
            
            response = self.session.get(mobile_url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            posts = self._extract_facebook_posts(soup, venue_name, url)
            
            return posts
            
        except Exception as e:
            print(f"Error scraping Facebook page {url}: {str(e)}")
            return []
    
    def _scrape_instagram_page(self, url: str, venue_name: str) -> List[Dict[str, Any]]:
        """Scrape Instagram page for job-related posts"""
        try:
            headers = {
                'User-Agent': random.choice(self.user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            }
            
            response = self.session.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            posts = self._extract_instagram_posts(soup, venue_name, url)
            
            return posts
            
        except Exception as e:
            print(f"Error scraping Instagram page {url}: {str(e)}")
            return []
    
    def _extract_facebook_posts(self, soup: BeautifulSoup, venue_name: str, base_url: str) -> List[Dict[str, Any]]:
        """Extract posts from Facebook page HTML"""
        posts = []
        
        # Look for post containers (mobile Facebook structure)
        post_containers = soup.find_all('div', {'data-ft': True}) or soup.find_all('article')
        
        for container in post_containers[:10]:  # Limit to recent posts
            post_text = container.get_text(strip=True)
            
            if len(post_text) < 20:  # Skip very short posts
                continue
            
            # Check for hiring keywords
            has_hiring_keywords = any(keyword.lower() in post_text.lower() for keyword in self.hiring_keywords)
            
            # Try to extract timestamp
            timestamp = self._extract_facebook_timestamp(container)
            
            # Try to extract post URL
            post_url = self._extract_facebook_post_url(container, base_url)
            
            posts.append({
                'venue_name': venue_name,
                'platform': 'facebook',
                'post_text': post_text[:500],  # Truncate long posts
                'post_url': post_url,
                'timestamp': timestamp,
                'has_hiring_keywords': has_hiring_keywords,
                'scraped_at': datetime.now().isoformat()
            })
        
        return posts
    
    def _extract_instagram_posts(self, soup: BeautifulSoup, venue_name: str, base_url: str) -> List[Dict[str, Any]]:
        """Extract posts from Instagram page HTML"""
        posts = []
        
        # Look for script tags containing post data
        script_tags = soup.find_all('script', type='application/ld+json')
        
        for script in script_tags:
            try:
                import json
                data = json.loads(script.string)
                
                # Extract posts from structured data
                if isinstance(data, dict) and 'mainEntityOfPage' in data:
                    # This is a simplified extraction - Instagram structure is complex
                    post_text = data.get('description', '')
                    
                    if len(post_text) > 20:
                        has_hiring_keywords = any(keyword.lower() in post_text.lower() for keyword in self.hiring_keywords)
                        
                        posts.append({
                            'venue_name': venue_name,
                            'platform': 'instagram',
                            'post_text': post_text[:500],
                            'post_url': base_url,
                            'timestamp': data.get('datePublished', ''),
                            'has_hiring_keywords': has_hiring_keywords,
                            'scraped_at': datetime.now().isoformat()
                        })
                        
            except json.JSONDecodeError:
                continue
        
        return posts
    
    def _extract_facebook_timestamp(self, container) -> str:
        """Extract timestamp from Facebook post container"""
        # Look for timestamp elements
        time_elements = container.find_all(['time', 'abbr'])
        
        for element in time_elements:
            if element.get('data-utime'):
                return element['data-utime']
            elif element.get('title'):
                return element['title']
        
        return ''
    
    def _extract_facebook_post_url(self, container, base_url: str) -> str:
        """Extract post URL from Facebook post container"""
        # Look for permalink links
        links = container.find_all('a', href=True)
        
        for link in links:
            href = link['href']
            if '/posts/' in href or '/story.php' in href:
                if href.startswith('/'):
                    return f"https://m.facebook.com{href}"
                return href
        
        return base_url
    
    def _load_venues(self) -> List[Dict[str, str]]:
        """Load venues from CSV"""
        venues_file = Path('data/venues.csv')
        if not venues_file.exists():
            return []
        
        with open(venues_file, 'r', encoding='utf-8') as f:
            return list(csv.DictReader(f))
    
    def _save_scraping_results(self, results: List[Dict[str, Any]]):
        """Save scraping results to CSV"""
        results_dir = Path('data/results')
        results_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = results_dir / f'social_scraping_{timestamp}.csv'
        
        if results:
            fieldnames = results[0].keys()
            with open(results_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)









