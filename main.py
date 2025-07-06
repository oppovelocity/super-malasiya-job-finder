#!/usr/bin/env python3

"""
Termux AI Outreach System - Main Orchestrator
Coordinates all outreach modules for automated lead generation
"""

import os
import sys
import json
import argparse
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional
import importlib.util
import traceback

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.logger import setup_logger
from utils.helpers import load_env, validate_input_data, save_results
from config.settings import SETTINGS

class OutreachOrchestrator:
    def __init__(self, mode='production'):
        self.mode = mode
        self.logger = setup_logger('main_orchestrator')
        self.results = {}
        self.failed_modules = []
        
        # Load environment variables
        load_env()
        
        # Available modules
        self.modules = {
            'twilio': 'modules.twilio_dialer',
            'telegram': 'modules.telegram_bot', 
            'social': 'modules.social_scraper',
            'whatsapp': 'modules.whatsapp_sender',
            'email': 'modules.email_harvester',
            'sentiment': 'modules.sentiment_analyzer'
        }
        
        self.logger.info(f"Initialized OutreachOrchestrator in {mode} mode")

    def load_module(self, module_name: str):
        """Dynamically load a module"""
        try:
            module_path = self.modules.get(module_name)
            if not module_path:
                raise ValueError(f"Module {module_name} not found")
            
            spec = importlib.util.spec_from_file_location(
                module_name, 
                f"{module_path.replace('.', '/')}.py"
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            return module
        except Exception as e:
            self.logger.error(f"Failed to load module {module_name}: {e}")
            return None

    def run_module(self, module_name: str, input_data: pd.DataFrame) -> Dict:
        """Run a single module with error handling"""
        self.logger.info(f"Starting module: {module_name}")
        
        try:
            module = self.load_module(module_name)
            if not module:
                return {'success': False, 'error': 'Module load failed'}
            
            # Get the main class from module
            class_name = self.get_class_name(module_name)
            if not hasattr(module, class_name):
                return {'success': False, 'error': f'Class {class_name} not found'}
            
            # Initialize and run module
            instance = getattr(module, class_name)(test_mode=(self.mode == 'test'))
            result = instance.run(input_data)
            
            self.logger.info(f"Module {module_name} completed successfully")
            return {
                'success': True,
                'result': result,
                'processed_count': len(input_data),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            error_msg = f"Module {module_name} failed: {str(e)}"
            self.logger.error(error_msg)
            self.logger.error(traceback.format_exc())
            
            self.failed_modules.append({
                'module': module_name,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
            
            return {'success': False, 'error': str(e)}

    def get_class_name(self, module_name: str) -> str:
        """Get the main class name for a module"""
        class_mapping = {
            'twilio': 'TwilioDialer',
            'telegram': 'TelegramBot',
            'social': 'SocialScraper',
            'whatsapp': 'WhatsAppSender',
            'email': 'EmailHarvester',
            'sentiment': 'SentimentAnalyzer'
        }
        return class_mapping.get(module_name, f"{module_name.title()}Module")

    def filter_data_for_module(self, data: pd.DataFrame, module_name: str) -> pd.DataFrame:
        """Filter input data based on module requirements"""
        if module_name == 'twilio':
            # Only records with valid phone numbers
            return data[data['phone'].notna() & (data['phone'] != '')]
        
        elif module_name == 'telegram':
            # Only records with telegram usernames or groups
            return data[data.get('telegram_username', '').notna()]
        
        elif module_name == 'social':
            # Only records with social media URLs
            social_cols = ['facebook_url', 'instagram_url', 'website']
            mask = data[social_cols].notna().any(axis=1)
            return data[mask]
        
        elif module_name == 'whatsapp':
            # Only records with WhatsApp numbers (usually same as phone)
            return data[data['phone'].notna() & (data['phone'] != '')]
        
        elif module_name == 'email':
            # Only records with websites for email harvesting
            return data[data['website'].notna() & (data['website'] != '')]
        
        elif module_name == 'sentiment':
            # All records with text content
            return data[data['description'].notna() | data['name'].notna()]
        
        return data

    def prioritize_leads(self, data: pd.DataFrame) -> pd.DataFrame:
        """Prioritize leads based on hiring score and other factors"""
        # Sort by hiring score if available
        if 'hiring_score' in data.columns:
            data = data.sort_values('hiring_score', ascending=False)
        
        # Apply daily limits to prevent spam
        limits = SETTINGS.get('daily_limits', {})
        
        limited_data = data.copy()
        for module_name, limit in limits.items():
            if len(limited_data) > limit:
                self.logger.info(f"Limiting {module_name} to {limit} leads per day")
                limited_data = limited_data.head(limit)
        
        return limited_data

    def run_full_pipeline(self, input_file: str, selected_modules: List[str] = None) -> Dict:
        """Run the complete outreach pipeline"""
        self.logger.info("Starting full outreach pipeline")
        
        try:
            # Load and validate input data
            input_data = pd.read_csv(input_file)
            if not validate_input_data(input_data):
                raise ValueError("Invalid input data format")
            
            # Prioritize leads
            prioritized_data = self.prioritize_leads(input_data)
            
            # Determine which modules to run
            modules_to_run = selected_modules or list(self.modules.keys())
            
            # Run each module
            for module_name in modules_to_run:
                if module_name not in self.modules:
                    self.logger.warning(f"Unknown module: {module_name}")
                    continue
                
                # Filter data for this module
                module_data = self.filter_data_for_module(prioritized_data, module_name)
                
                if len(module_data) == 0:
                    self.logger.warning(f"No suitable data for module: {module_name}")
                    continue
                
                # Run module
                result = self.run_module(module_name, module_data)
                self.results[module_name] = result
                
                # Add delay between modules to avoid rate limiting
                if self.mode == 'production':
                    import time
                    time.sleep(SETTINGS.get('module_delay', 30))
            
            # Generate summary report
            summary = self.generate_summary()
            
            # Save results
            self.save_session_results(input_file, summary)
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Pipeline failed: {str(e)}")
            self.logger.error(traceback.format_exc())
            return {'success': False, 'error': str(e)}

    def generate_summary(self) -> Dict:
        """Generate a summary of the pipeline run"""
        successful_modules = [k for k, v in self.results.items() if v.get('success')]
        failed_modules = [k for k, v in self.results.items() if not v.get('success')]
        
        total_processed = sum(v.get('processed_count', 0) for v in self.results.values())
        
        summary = {
            'timestamp': datetime.now().isoformat(),
            'mode': self.mode,
            'total_modules': len(self.results),
            'successful_modules': len(successful_modules),
            'failed_modules': len(failed_modules),
            'total_leads_processed': total_processed,
            'success_rate': len(successful_modules) / len(self.results) * 100 if self.results else 0,
            'module_results': self.results,
            'failed_module_details': self.failed_modules
        }
        
        return summary

    def save_session_results(self, input_file: str, summary: Dict):
        """Save session results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save detailed results
        results_file = f"data/output/session_results_{timestamp}.json"
        os.makedirs(os.path.dirname(results_file), exist_ok=True)
        
        with open(results_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        self.logger.info(f"Session results saved to: {results_file}")

    def retry_failed_modules(self, input_file: str) -> Dict:
        """Retry modules that failed in the last run"""
        if not self.failed_modules:
            self.logger.info("No failed modules to retry")
            return {'success': True, 'message': 'No failed modules'}
        
        self.logger.info(f"Retrying {len(self.failed_modules)} failed modules")
        
        failed_module_names = [m['module'] for m in self.failed_modules]
        return self.run_full_pipeline(input_file, failed_module_names)

def main():
    parser = argparse.ArgumentParser(description='Termux AI Outreach System')
    parser.add_argument('--mode', choices=['production', 'test'], default='production',
                       help='Run mode: production or test')
    parser.add_argument('--input', required=True, help='Input CSV file path')
    parser.add_argument('--modules', help='Comma-separated list of modules to run')
    parser.add_argument('--retry-failed', action='store_true', 
                       help='Retry only failed modules from last run')
    parser.add_argument('--config', help='Custom config file path')
    
    args = parser.parse_args()
    
    # Initialize orchestrator
    orchestrator = OutreachOrchestrator(mode=args.mode)
    
    # Parse selected modules
    selected_modules = None
    if args.modules:
        selected_modules = [m.strip() for m in args.modules.split(',')]
    
    # Run pipeline
    if args.retry_failed:
        result = orchestrator.retry_failed_modules(args.input)
    else:
        result = orchestrator.run_full_pipeline(args.input, selected_modules)
    
    # Print summary
    print("\n" + "="*50)
    print("OUTREACH PIPELINE SUMMARY")
    print("="*50)
    print(f"Mode: {result.get('mode', 'unknown')}")
    print(f"Total Leads Processed: {result.get('total_leads_processed', 0)}")
    print(f"Successful Modules: {result.get('successful_modules', 0)}")
    print(f"Failed Modules: {result.get('failed_modules', 0)}")
    print(f"Success Rate: {result.get('success_rate', 0):.1f}%")
    
    if result.get('failed_module_details'):
        print("\nFailed Modules:")
        for failure in result['failed_module_details']:
            print(f"  - {failure['module']}: {failure['error']}")
    
    print("="*50)
    
    # Exit with appropriate code
    sys.exit(0 if result.get('success_rate', 0) > 50 else 1)

if __name__ == "__main__":
    main()
