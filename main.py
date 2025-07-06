
# =============================================================================
# MAIN.PY - ORCHESTRATOR
# =============================================================================

import os
import sys
import json
import logging
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from utils.logger import setup_logger
from utils.helpers import load_config, save_results
from modules.twilio_dialer import TwilioDialer
from modules.telegram_bot import TelegramBot
from modules.social_scraper import SocialScraper
from modules.whatsapp_sender import WhatsAppSender
from modules.email_harvester import EmailHarvester
from modules.sentiment_analyzer import SentimentAnalyzer

class OutreachOrchestrator:
    """Main orchestrator for the AI outreach system"""
    
    def __init__(self):
        self.config = load_config()
        self.logger = setup_logger('main')
        self.results = {}
        self.failed_modules = []
        
    def run_daily_campaign(self) -> Dict[str, Any]:
        """Execute the complete daily outreach campaign"""
        campaign_start = datetime.now()
        self.logger.info(f"Starting daily campaign at {campaign_start}")
        
        # Module execution order
        modules = [
            ('social_scraper', self._run_social_scraper),
            ('sentiment_analyzer', self._run_sentiment_analyzer),
            ('email_harvester', self._run_email_harvester),
            ('telegram_bot', self._run_telegram_bot),
            ('whatsapp_sender', self._run_whatsapp_sender),
            ('twilio_dialer', self._run_twilio_dialer),
        ]
        
        for module_name, module_func in modules:
            try:
                self.logger.info(f"Starting module: {module_name}")
                result = module_func()
                self.results[module_name] = {
                    'status': 'success',
                    'data': result,
                    'timestamp': datetime.now().isoformat()
                }
                self.logger.info(f"Module {module_name} completed successfully")
                
            except Exception as e:
                self.logger.error(f"Module {module_name} failed: {str(e)}")
                self.logger.error(traceback.format_exc())
                self.failed_modules.append(module_name)
                self.results[module_name] = {
                    'status': 'failed',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
        
        # Retry failed modules once
        if self.failed_modules:
            self.logger.info(f"Retrying failed modules: {self.failed_modules}")
            self._retry_failed_modules()
        
        # Save daily results
        self._save_daily_results()
        
        campaign_end = datetime.now()
        duration = campaign_end - campaign_start
        
        self.logger.info(f"Campaign completed in {duration}")
        return self.results
    
    def _run_social_scraper(self) -> Dict[str, Any]:
        """Run social media scraping"""
        scraper = SocialScraper(self.config)
        return scraper.scrape_venues()
    
    def _run_sentiment_analyzer(self) -> Dict[str, Any]:
        """Run sentiment analysis on scraped content"""
        analyzer = SentimentAnalyzer(self.config)
        return analyzer.analyze_scraped_content()
    
    def _run_email_harvester(self) -> Dict[str, Any]:
        """Run email harvesting"""
        harvester = EmailHarvester(self.config)
        return harvester.harvest_emails()
    
    def _run_telegram_bot(self) -> Dict[str, Any]:
        """Run Telegram bot messaging"""
        bot = TelegramBot(self.config)
        return bot.send_messages()
    
    def _run_whatsapp_sender(self) -> Dict[str, Any]:
        """Run WhatsApp messaging"""
        sender = WhatsAppSender(self.config)
        return sender.send_messages()
    
    def _run_twilio_dialer(self) -> Dict[str, Any]:
        """Run Twilio auto-dialer"""
        dialer = TwilioDialer(self.config)
        return dialer.make_calls()
    
    def _retry_failed_modules(self):
        """Retry failed modules once"""
        retry_modules = self.failed_modules.copy()
        self.failed_modules = []
        
        for module_name in retry_modules:
            try:
                self.logger.info(f"Retrying module: {module_name}")
                module_func = getattr(self, f'_run_{module_name}')
                result = module_func()
                self.results[module_name] = {
                    'status': 'success_retry',
                    'data': result,
                    'timestamp': datetime.now().isoformat()
                }
                self.logger.info(f"Module {module_name} retry successful")
                
            except Exception as e:
                self.logger.error(f"Module {module_name} retry failed: {str(e)}")
                self.failed_modules.append(module_name)
    
    def _save_daily_results(self):
        """Save daily campaign results"""
        results_dir = PROJECT_ROOT / 'data' / 'results'
        results_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = results_dir / f'campaign_{timestamp}.json'
        
        campaign_summary = {
            'timestamp': timestamp,
            'modules_run': len(self.results),
            'successful_modules': len([r for r in self.results.values() if r['status'] in ['success', 'success_retry']]),
            'failed_modules': self.failed_modules,
            'results': self.results
        }
        
        save_results(campaign_summary, str(results_file))
        self.logger.info(f"Campaign results saved to {results_file}")

def main():
    """Main entry point"""
    orchestrator = OutreachOrchestrator()
    results = orchestrator.run_daily_campaign()
    
    # Print summary
    successful = len([r for r in results.values() if r['status'] in ['success', 'success_retry']])
    total = len(results)
    print(f"\n=== CAMPAIGN SUMMARY ===")
    print(f"Modules executed: {total}")
    print(f"Successful: {successful}")
    print(f"Failed: {total - successful}")
    
    if orchestrator.failed_modules:
        print(f"Failed modules: {', '.join(orchestrator.failed_modules)}")
    
    return 0 if not orchestrator.failed_modules else 1

if __name__ == "__main__":
    sys.exit(main())
