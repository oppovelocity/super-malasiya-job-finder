#MODULES/SENTIMENT_ANALYZER.PY - SENTIMENT ANALYZER

import csv
import json
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path
import re

class SentimentAnalyzer:
"""Sentiment analyzer for hiring urgency detection"""

def __init__(self, config: Dict[str, Any]):  
    self.config = config  
    self.analyzer_config = config.get('sentiment_analyzer', {})  
      
    # Urgency keywords with weights  
    self.urgency_keywords = {  
        'urgent': 5,  
        'asap': 5,  
        'immediately': 5,  
        'now hiring': 4,  
        'hiring now': 4,  
        'start immediately': 4,  
        'needed now': 4,  
        'hiring': 3,  
        'join us': 3,  
        'apply now': 3,  
        'vacancy': 3,  
        'position': 2,  
        'job': 2,  
        'career': 2,  
        'opportunity': 2,  
        'staff': 2,  
        'team': 2,  
        'recruit': 2,  
        'wanted': 2,  
        'looking for': 2,  
    }  
      
    # Negative keywords that reduce urgency  
    self.negative_keywords = {  
        'no longer': -3,  
        'closed': -2,  
        'filled': -2,  
        'not hiring': -4,  
        'no vacancy': -3,  
        'full': -2,  
    }  
      
    # Boost keywords that increase urgency  
    self.boost_keywords = {  
        'multiple': 1.5,  
        'several': 1.3,  
        'many': 1.3,  
        'full time': 1.2,  
        'part time': 1.1,  
        'experienced': 1.2,  
        'skilled': 1.2,  
    }  
  
def analyze_scraped_content(self) -> Dict[str, Any]:  
    """Analyze sentiment of all scraped social media content"""  
    scraped_files = self._find_scraped_files()  
    results = []  
      
    for file_path in scraped_files:  
        file_results = self._analyze_file(file_path)  
        results.extend(file_results)  
      
    # Save analyzed results  
    self._save_analysis_results(results)  
      
    # Generate summary  
    summary = self._generate_summary(results)  
      
    return {  
        'total_posts_analyzed': len(results),  
        'high_urgency_posts': len([r for r in results if r['urgency_score'] >= 4]),  
        'medium_urgency_posts': len([r for r in results if 2 <= r['urgency_score'] < 4]),  
        'low_urgency_posts': len([r for r in results if r['urgency_score'] < 2]),  
        'summary': summary,  
        'results': results  
    }  
  
def _analyze_file(self, file_path: Path) -> List[Dict[str, Any]]:  
    """Analyze a single scraped file"""  
    results = []  
      
    try:  
        with open(file_path, 'r', encoding='utf-8') as f:  
            reader = csv.DictReader(f)  
              
            for row in reader:  
                post_text = row.get('post_text', '')  
                  
                if not post_text or len(post_text) < 10:  
                    continue  
                  
                analysis = self._analyze_post(post_text)  
                  
                result = {  
                    'venue_name': row.get('venue_name', ''),  
                    'platform': row.get('platform', ''),  
                    'post_text': post_text,  
                    'post_url': row.get('post_url', ''),  
                    'original_timestamp': row.get('timestamp', ''),  
                    'urgency_score': analysis['urgency_score'],  
                    'urgency_level': analysis['urgency_level'],  
                    'detected_keywords': analysis['detected_keywords'],  
                    'confidence': analysis['confidence'],  
                    'analysis_timestamp': datetime.now().isoformat()  
                }  
                  
                results.append(result)  
                  
    except Exception as e:  
        print(f"Error analyzing file {file_path}: {str(e)}")  
      
    return results  
  
def _analyze_post(self, post_text: str) -> Dict[str, Any]:  
    """Analyze sentiment and urgency of a single post"""  
    text_lower = post_text.lower()  
      
    # Calculate base urgency score  
    urgency_score = 0  
    detected_keywords = []  
      
    # Check for urgency keywords  
    for keyword, weight in self.urgency_keywords.items():  
        if keyword in text_lower:  
            urgency_score += weight  
            detected_keywords.append(keyword)  
      
    # Check for negative keywords  
    for keyword, weight in self.negative_keywords.items():  
        if keyword in text_lower:  
            urgency_score += weight  # weight is negative  
            detected_keywords.append(f"negative:{keyword}")  
      
    # Apply boost multipliers  
    boost_multiplier = 1.0  
    for keyword, multiplier in self.boost_keywords.items():  
        if keyword in text_lower:  
            boost_multiplier *= multiplier  
            detected_keywords.append(f"boost:{keyword}")  
      
    urgency_score *= boost_multiplier  
      
    # Ensure score is between 0 and 5  
    urgency_score = max(0, min(5, urgency_score))  
      
    # Determine urgency level  
    if urgency_score >= 4:  
        urgency_level = 'high'  
    elif urgency_score >= 2:  
        urgency_level = 'medium'  
    else:  
        urgency_level = 'low'  
      
    # Calculate confidence based on number of keywords found  
    confidence = min(1.0, len(detected_keywords) / 5.0)  
      
    return {  
        'urgency_score': round(urgency_score, 2),  
        'urgency_level': urgency_level,  
        'detected_keywords': detected_keywords,  
        'confidence': round(confidence, 2)  
    }  
  
def _find_scraped_files(self) -> List[Path]:  
    """Find all scraped social media files"""  
    results_dir = Path('data/results')  
    if not results_dir.exists():  
        return []  
      
    scraped_files = []  
    for file_path in results_dir.glob('social_scraping_*.csv'):  
        scraped_files.append(file_path)  
      
    return scraped_files  
  
def _generate_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:  
    """Generate analysis summary"""  
    if not results:  
        return {}  
      
    # Group by venue  
    venue_scores = {}  
    for result in results:  
        venue = result['venue_name']  
        if venue not in venue_scores:  
            venue_scores[venue] = []  
        venue_scores[venue].append(result['urgency_score'])  
      
    # Calculate average scores per venue  
    venue_averages = {}  
    for venue, scores in venue_scores.items():  
        venue_averages[venue] = sum(scores) / len(scores)  
      
    # Find top urgent venues  
    top_urgent = sorted(venue_averages.items(), key=lambda x: x[1], reverse=True)[:10]  
      
    return {  
        'total_venues': len(venue_scores),  
        'average_urgency_score': sum(result['urgency_score'] for result in results) / len(results),  
        'top_urgent_venues': [{'venue': venue, 'score': score} for venue, score in top_urgent],  
        'high_urgency_venues': [venue for venue, score in venue_averages.items() if score >= 4]  
    }  
  
def _save_analysis_results(self, results: List[Dict[str, Any]]):  
    """Save analysis results to CSV"""  
    results_dir = Path('data/results')  
    results_dir.mkdir(exist_ok=True)  
      
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')  
    results_file = results_dir / f'sentiment_analysis_{timestamp}.csv'  
      
    if results:  
        fieldnames = results[0].keys()  
        with open(results_file, 'w', newline='', encoding='utf-8') as f:  
            writer = csv.DictWriter(f, fieldnames=fieldnames)  
            writer.writeheader()  
            writer.writerows(results)