# =============================================================================
# UTILS/HELPERS.PY - COMMON HELPER FUNCTIONS
# =============================================================================

import json
import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

def load_config() -> Dict[str, Any]:
    """Load configuration from environment variables and config files"""
    
    # Load environment variables
    env_file = Path('config/.env')
    if env_file.exists():
        load_dotenv(env_file)
    
    # Load JSON config
    config_file = Path('config/settings.json')
    if config_file.exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
    else:
        config = {}
    
    # Override with environment variables
    config.update({
        'twilio': {
            'account_sid': os.getenv('TWILIO_ACCOUNT_SID', ''),
            'auth_token': os.getenv('TWILIO_AUTH_TOKEN', ''),
            'from_number': os.getenv('TWILIO_FROM_NUMBER', ''),
            'voice_message_url': os.getenv('TWILIO_VOICE_MESSAGE_URL', ''),
            'max_retries': int(os.getenv('TWILIO_MAX_RETRIES', '3')),
            'delay_between_calls': int(os.getenv('TWILIO_DELAY_BETWEEN_CALLS', '30'))
        },
        'telegram': {
            'bot_token': os.getenv('TELEGRAM_BOT_TOKEN', ''),
            'message_template': os.getenv('TELEGRAM_MESSAGE_TEMPLATE', ''),
            'delay_min': int(os.getenv('TELEGRAM_DELAY_MIN', '30')),
            'delay_max': int(os.getenv('TELEGRAM_DELAY_MAX', '60')),
            'max_retries': int(os.getenv('TELEGRAM_MAX_RETRIES', '3'))
        },
        'whatsapp': {
            'access_token': os.getenv('WHATSAPP_ACCESS_TOKEN', ''),
            'phone_number_id': os.getenv('WHATSAPP_PHONE_NUMBER_ID', ''),
            'message_template': os.getenv('WHATSAPP_MESSAGE_TEMPLATE', ''),
            'delay_min': int(os.getenv('WHATSAPP_DELAY_MIN', '30')),
            'delay_max': int(os.getenv('WHATSAPP_DELAY_MAX', '60')),
            'max_retries': int(os.getenv('WHATSAPP_MAX_RETRIES', '3'))
        },
        'social_scraper': {
            'hiring_keywords': os.getenv('HIRING_KEYWORDS', '').split(',') if os.getenv('HIRING_KEYWORDS') else [],
            'delay_min': int(os.getenv('SCRAPER_DELAY_MIN', '10')),
            'delay_max': int(os.getenv('SCRAPER_DELAY_MAX', '30')),
            'user_agents': []
        },
        'email_harvester': {
            'timeout': int(os.getenv('EMAIL_HARVESTER_TIMEOUT', '15')),
            'delay_min': int(os.getenv('EMAIL_HARVESTER_DELAY_MIN', '5')),
            'delay_max': int(os.getenv('EMAIL_HARVESTER_DELAY_MAX', '15')),
            'user_agents': []
        }
    })
    
    return config

def save_results(data: Dict[str, Any], filepath: str):
    """Save results to JSON file"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def create_directory_structure():
    """Create the required directory structure"""
    directories = [
        'config',
        'modules',
        'data',
        'data/results',
        'logs',
        'logs/daily_logs',
        'utils'
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        
        # Create __init__.py for Python packages
        if directory in ['modules', 'utils']:
            init_file = Path(directory) / '__init__.py'
            if not init_file.exists():
                init_file.touch()