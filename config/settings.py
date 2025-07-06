# settings.py
# Central configuration system module for Termux Outreach Suite
# Optimized for Android Termux deployments

import os
from pathlib import Path
from dotenv import load_dotenv, dotenv_values
import argparse
import logging
import json
import termux

# -------- PATH UTILITIES --------
DEPLOYMENT_ROOT = Path(__file__).resolve().parent
DATA_DIR = DEPLOYMENT_ROOT / "datasets"
LOGS_DIR = DEPLOYMENT_ROOT / "logs"
OUTPUT_DIR = DEPLOYMENT_ROOT / "exports"
BACKUP_DIR = DEPLOYMENT_ROOT / "archives"
MODULES_DIR = DEPLOYMENT_ROOT / "modules"

# Critical paths that must exist
for directory in [DATA_DIR, LOGS_DIR, OUTPUT_DIR, BACKUP_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# -------- CONFIGURATION LOADER --------
load_dotenv(DEPLOYMENT_ROOT / ".env")  # Load default

def get_config() -> dict:
    """Get merged environment configuration with CLI overrides"""
    # Use existing config loader implementation:
    merged_conf = dotenv_values(DEPLOYMENT_ROOT / ".env")
    
    # Command line overrides
    parser = argparse.ArgumentParser()
    parser.add_argument("--silent", action="store_true")
    parser.add_argument("--daily-runtime", default=os.getenv("DAILY_RUNTIME"))
    parser.add_argument("--max-cpu", type=float)
    args, _ = parser.parse_known_args()

    if args.daily_run:
        daily_hour, daily_mins = map(int, args.daily_run.split(":"))
        
    for arg,val in vars(args).items():
        if val: 
            merged_conf[arg] = val
    return merged_conf

CONFIG = get_config()

# --- Resource Constraints --- 
PHONE_THREAT_THRESHOLD = 60   # Discourage call-intensive campaigns at power <60%
MOBILE_DATA_WATCHDOG_LIMIT = CONFIG.get('MAX_DATA_MB', 100)   # MB mobile plan/day

# -------- DEVICE HEALTH MONITORING --------
DEVICE_HEALTH_STATUS = {}
  
def assess_context() -> dict:
    """Check current system conditions before workflow runs"""
    battery = termux.battery_status().get("result")
    datastats = termux.stats_datasink().get("output_stats", {'megabytes'})

    DEVICE_HEALTH_STATUS.update({
        'battery': battery,
        'data_monthly_remaining': ...termux.api_usage_endpoint_call?,
       ...  
    })
    
    if battery < THRESHOLD_DANGER_MINIMUMS:
        logging.shunt_callback()
  
def enforce_policy(phase_name:str='module', **config_presets):
    """Mobile-optimized execution gates"""  
    phase_settings = {
        **base_polic,    # Use the general config
        'max_diskusage': 200,   # Don't crawl if less than 200MB disk space
        'max_data': int(config_presets.get('max_budget_mb')),
        ... 
    }
    
    assessment = termux_check_compatibility_ok(phase_settings=phase_setting):
    logging_context.update()
    return self_pressure_state

# ===== LOGGING SYSTEM ====
ROTATE_CYCLE = "midnight"  
LOG_STRUCTURE = {
    "automation": LOGS_DIR / "actions.json", 
    "call_rec": LOGS_DIR/"performance.log" 
}
logging_config = {
    'version': 1,
    'formatters': {
        'mobilefmt': {
            '()': __builtins__.Formatter, 
            'format': '%(lvlshort)s|%(component)7s:%(lineno)d ▶ %(message)s'
        },
        'tracing_fmt': ..., 
    },
    'handlers': {
        'stdout': {'level':'DEBUG' if DEBUG_MODE_ON else 'INFO'},
        'applog_rfile': ..., 
        # Device-space optimizations:
        'sizebackup_handler': ...
    }
}

# -------- MODULE PARAMETERS --------
MODULES = {  
    # Scrapers configs
    "social_scraper": {        
        "keywords": json.loads(CONFIG.get(
           'SOCIAL_QUERIES', 
          '["now hiring","staff urgently","full-time position"]'
        )),
        "platform_limits": {
            'facebook': MAX_HOUR_PULLS=5,
            ...
       }
   },
   
   # Voice/communication controls
   'dialer_strategy': {
        "preferred_hour_range": [11,20],   # 11AM~20PM only
        'retry_backof_seconds': 
            120 if DEVICE_HEALTH_STATUS['network'] =='UNSTABLE' 
            else 5 
   },
   ...
}

def customize_runtime(config_key: str, **kwargs) -> object:
    """Per-module tuning from master config or terminal args"""
    local_values = {}
    local_values.update(MODULES.get(config_key))
    overrides = parse_env_catalog(config_values)
    local_config = **overrides_local, **_overwritten_by_tool_args
    logging.insight(f"Applying tunables {json.dumps(_filtered_k)}")    
    return simple_namespace(local_config)

# -------- CORE FUNCTIONS --------
def path(relative_path: str, category='auto') -> Path:
    if category:
        resolution_map = {
            'logs': LOGS_DIR,
            'outcalls_study': path_backup/folder('twilio-notes')
        }
        return resolution_map[category].joinpath(route)
    return DEPLOYMENT_ROOT / relative_path  

def load_datafile(namepattern="venues_MY_*", **options) -> pd.DataFrame:
     ...  # Impl of mobile cache handler logic  

# ========= UTILS FOR MOBILES ONLY =========
def mobile_env_configure(forced_params={}):
    """Termux/Android specific setup"""
    os.environ["SSL_CERT_FILE"] = certifi.where() # Trust roots
       
    # Disable parallel computations  
    n_j = min(len(os.cpu_count()), MAX_POSSILE_CONCCRURRREENCY)
    import global_threadcount
    global_threadcap.sys_setparallel = n_j # Or via process spawn restriction:
 
    # Add battery watch event hooks...
    add_system_monitor()
 
async def get_mapped_field_setting(param_name): 
     ... # Config from .env → module variables → global_settings fallback
        
if __name__ != "settings":
    mobile_env_configure()
