automate_daily.py
import os
import subprocess
import logging
from datetime import datetime, time
import asyncio
import schedule

class DailyAutomation:
    def __init__(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('automation.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def run_venue_scraper(self):
        try:
            result = subprocess.run(['bash', 'get_malaysia_venues.sh'], 
                                  capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                self.logger.info("✓ Venue scraper completed")
                return True
            else:
                self.logger.error(f"✗ Venue scraper failed: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            self.logger.error("✗ Venue scraper timed out")
            return False
    
    def run_job_detector(self):
        try:
            result = subprocess.run(['python', 'job_signal_detector.py'], 
                                  capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                self.logger.info("✓ Job detector completed")
                return True
            else:
                self.logger.error(f"✗ Job detector failed: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            self.logger.error("✗ Job detector timed out")
            return False
    
    async def run_telegram_bot(self):
        try:
            result = subprocess.run(['python', 'telegram_lead_bot.py'], 
                                  capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                self.logger.info("✓ Telegram bot completed")
                return True
            else:
                self.logger.error(f"✗ Telegram bot failed: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            self.logger.error("✗ Telegram bot timed out")
            return False
    
    def run_voice_generator(self):
        try:
            result = subprocess.run(['python', 'voice_followup.py'], 
                                  capture_output=True, text=True, timeout=180)
            if result.returncode == 0:
                self.logger.info("✓ Voice generator completed")
                return True
            else:
                self.logger.error(f"✗ Voice generator failed: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            self.logger.error("✗ Voice generator timed out")
            return False
    
    async def execute_pipeline(self):
        self.logger.info("🚀 Starting daily automation pipeline")
        
        success_count = 0
        
        if self.run_venue_scraper():
            success_count += 1
            
            if self.run_job_detector():
                success_count += 1
                
                if os.path.exists('hiring_leads.csv'):
                    if await self.run_telegram_bot():
                        success_count += 1
                    
                    if self.run_voice_generator():
                        success_count += 1
        
        self.logger.info(f"📊 Pipeline completed: {success_count}/4 modules successful")
        return success_count >= 2

def daily_job():
    automation = DailyAutomation()
    asyncio.run(automation.execute_pipeline())

if __name__ == "__main__":
    schedule.every().day.at("09:00").do(daily_job)
    schedule.every().day.at("15:00").do(daily_job)
    
    while True:
        schedule.run_pending()
        asyncio.sleep(3600)
