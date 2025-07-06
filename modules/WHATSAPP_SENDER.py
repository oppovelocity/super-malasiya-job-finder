# =============================================================================
# MODULES/WHATSAPP_SENDER.PY - WHATSAPP BUSINESS API
# =============================================================================

import csv
import time
import random
import requests
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path

class WhatsAppSender:
    """WhatsApp Business API sender for venue outreach"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.whatsapp_config = config.get('whatsapp', {})
        self.access_token = self.whatsapp_config.get('access_token')
        self.phone_number_id = self.whatsapp_config.get('phone_number_id')
        self.base_url = f"https://graph.facebook.com/v18.0/{self.phone_number_id}/messages"
        self.message_template = self.whatsapp_config.get('message_template', '')
        self.delay_min = self.whatsapp_config.get('delay_min', 30)
        self.delay_max = self.whatsapp_config.get('delay_max', 60)
        self.max_retries = self.whatsapp_config.get('max_retries', 3)
    
    def send_messages(self) -> Dict[str, Any]:
        """Send WhatsApp messages to all business numbers"""
        targets = self._load_whatsapp_targets()
        results = []
        
        for i, target_data in enumerate(targets):
            phone_number = target_data.get('phone_number')
            venue_name = target_data.get('venue_name', 'Unknown')
            
            if not phone_number:
                continue
            
            # Add random delay
            if i > 0:
                delay = random.randint(self.delay_min, self.delay_max)
                time.sleep(delay)
            
            message = self._customize_message(venue_name, target_data)
            result = self._send_message(phone_number, message, venue_name)
            results.append(result)
            
            # Log result
            self._log_message_result(result)
        
        # Save results
        self._save_message_results(results)
        
        return {
            'total_messages': len(results),
            'successful_messages': len([r for r in results if r['status'] == 'success']),
            'failed_messages': len([r for r in results if r['status'] == 'failed']),
            'results': results
        }
    
    def _send_message(self, phone_number: str, message: str, venue_name: str) -> Dict[str, Any]:
        """Send a single WhatsApp message with retry logic"""
        for attempt in range(self.max_retries):
            try:
                payload = {
                    "messaging_product": "whatsapp",
                    "to": phone_number,
                    "type": "text",
                    "text": {
                        "body": message
                    }
                }
                
                headers = {
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json"
                }
                
                response = requests.post(self.base_url, json=payload, headers=headers, timeout=30)
                response.raise_for_status()
                
                response_data = response.json()
                
                return {
                    'phone_number': phone_number,
                    'venue_name': venue_name,
                    'status': 'success',
                    'message_id': response_data.get('messages', [{}])[0].get('id', ''),
                    'attempt': attempt + 1,
                    'timestamp': datetime.now().isoformat()
                }
                
            except Exception as e:
                if attempt == self.max_retries - 1:
                    return {
                        'phone_number': phone_number,
                        'venue_name': venue_name,
                        'status': 'failed',
                        'error': str(e),
                        'attempts': self.max_retries,
                        'timestamp': datetime.now().isoformat()
                    }
                time.sleep(5)  # Wait before retry
    
    def _customize_message(self, venue_name: str, target_data: Dict[str, Any]) -> str:
        """Customize message template with venue data"""
        message = self.message_template
        
        # Replace placeholders
        replacements = {
            '{venue_name}': venue_name,
            '{phone_number}': target_data.get('phone_number', ''),
            '{location}': target_data.get('location', ''),
            '{contact_name}': target_data.get('contact_name', ''),
        }
        
        for placeholder, value in replacements.items():
            message = message.replace(placeholder, value)
        
        return message
    
    def _load_whatsapp_targets(self) -> List[Dict[str, str]]:
        """Load WhatsApp targets from CSV"""
        targets_file = Path('data/whatsapp_targets.csv')
        if not targets_file.exists():
            return []
        
        with open(targets_file, 'r', encoding='utf-8') as f:
            return list(csv.DictReader(f))
    
    def _log_message_result(self, result: Dict[str, Any]):
        """Log individual message result"""
        status = result['status']
        phone = result['phone_number']
        venue = result['venue_name']
        
        if status == 'success':
            print(f"✓ Sent WhatsApp to {venue} ({phone}) - ID: {result.get('message_id', 'N/A')}")
        else:
            print(f"✗ Failed WhatsApp to {venue} ({phone}) - Error: {result['error']}")
    
    def _save_message_results(self, results: List[Dict[str, Any]]):
        """Save message results to CSV"""
        results_dir = Path('data/results')
        results_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = results_dir / f'whatsapp_messages_{timestamp}.csv'
        
        if results:
            fieldnames = results[0].keys()
            with open(results_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)
