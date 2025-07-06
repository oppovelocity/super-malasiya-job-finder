# =============================================================================
# MODULES/TELEGRAM_BOT.PY - TELEGRAM DM BOT
# =============================================================================

import csv
import time
import random
import asyncio
from datetime import datetime
from typing import List, Dict, Any
from telegram import Bot
from telegram.error import TelegramError
from pathlib import Path

class TelegramBot:
    """Telegram bot for automated messaging"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.telegram_config = config.get('telegram', {})
        self.bot_token = self.telegram_config.get('bot_token')
        self.bot = Bot(token=self.bot_token)
        self.message_template = self.telegram_config.get('message_template', '')
        self.delay_min = self.telegram_config.get('delay_min', 30)
        self.delay_max = self.telegram_config.get('delay_max', 60)
        self.max_retries = self.telegram_config.get('max_retries', 3)
    
    def send_messages(self) -> Dict[str, Any]:
        """Send messages to all Telegram targets"""
        return asyncio.run(self._send_messages_async())
    
    async def _send_messages_async(self) -> Dict[str, Any]:
        """Async message sending"""
        targets = self._load_telegram_targets()
        results = []
        
        for i, target_data in enumerate(targets):
            username = target_data.get('username')
            venue_name = target_data.get('venue_name', 'Unknown')
            
            if not username:
                continue
            
            # Add random delay to avoid spam detection
            if i > 0:
                delay = random.randint(self.delay_min, self.delay_max)
                await asyncio.sleep(delay)
            
            message = self._customize_message(venue_name, target_data)
            result = await self._send_message(username, message, venue_name)
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
    
    async def _send_message(self, username: str, message: str, venue_name: str) -> Dict[str, Any]:
        """Send a single message with retry logic"""
        for attempt in range(self.max_retries):
            try:
                # Try to send message (requires chat_id, not username)
                # In practice, you'd need to resolve username to chat_id first
                chat_id = await self._resolve_username_to_chat_id(username)
                
                if chat_id:
                    await self.bot.send_message(chat_id=chat_id, text=message)
                    
                    return {
                        'username': username,
                        'venue_name': venue_name,
                        'status': 'success',
                        'message_length': len(message),
                        'attempt': attempt + 1,
                        'timestamp': datetime.now().isoformat()
                    }
                else:
                    return {
                        'username': username,
                        'venue_name': venue_name,
                        'status': 'failed',
                        'error': 'Could not resolve username to chat_id',
                        'attempts': attempt + 1,
                        'timestamp': datetime.now().isoformat()
                    }
                    
            except TelegramError as e:
                if attempt == self.max_retries - 1:
                    return {
                        'username': username,
                        'venue_name': venue_name,
                        'status': 'failed',
                        'error': str(e),
                        'attempts': self.max_retries,
                        'timestamp': datetime.now().isoformat()
                    }
                await asyncio.sleep(5)  # Wait before retry
    
    async def _resolve_username_to_chat_id(self, username: str) -> str:
        """Resolve username to chat_id (simplified - in practice more complex)"""
        # This is a simplified version - in practice you'd need to:
        # 1. Use the Telegram API to search for the user
        # 2. Handle the fact that users must have interacted with bot first
        # 3. Or use a userbot library like pyrogram for direct messaging
        
        # For now, return None to indicate failure
        return None
    
    def _customize_message(self, venue_name: str, target_data: Dict[str, Any]) -> str:
        """Customize message template with venue data"""
        message = self.message_template
        
        # Replace placeholders
        replacements = {
            '{venue_name}': venue_name,
            '{username}': target_data.get('username', ''),
            '{location}': target_data.get('location', ''),
            '{contact_name}': target_data.get('contact_name', ''),
        }
        
        for placeholder, value in replacements.items():
            message = message.replace(placeholder, value)
        
        return message
    
    def _load_telegram_targets(self) -> List[Dict[str, str]]:
        """Load Telegram targets from CSV"""
        targets_file = Path('data/telegram_targets.csv')
        if not targets_file.exists():
            return []
        
        with open(targets_file, 'r', encoding='utf-8') as f:
            return list(csv.DictReader(f))
    
    def _log_message_result(self, result: Dict[str, Any]):
        """Log individual message result"""
        status = result['status']
        username = result['username']
        venue = result['venue_name']
        
        if status == 'success':
            print(f"✓ Sent message to {venue} (@{username})")
        else:
            print(f"✗ Failed to message {venue} (@{username}) - Error: {result['error']}")
    
    def _save_message_results(self, results: List[Dict[str, Any]]):
        """Save message results to CSV"""
        results_dir = Path('data/results')
        results_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = results_dir / f'telegram_messages_{timestamp}.csv'
        
        if results:
            fieldnames = results[0].keys()
            with open(results_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(results)


