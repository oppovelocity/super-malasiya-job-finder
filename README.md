# Termux AI Outreach System - Project Structure

## 📁 Directory Structure
```
termux_outreach_ai/
├── main.py                 # Central orchestrator
├── config/
│   ├── .env.template       # Environment variables template
│   └── settings.py         # Configuration management
├── modules/
│   ├── __init__.py
│   ├── twilio_dialer.py    # Voice call automation
│   ├── telegram_bot.py     # Telegram messaging
│   ├── social_scraper.py   # Facebook/Instagram scraper
│   ├── whatsapp_sender.py  # WhatsApp messaging
│   ├── email_harvester.py  # Email extraction
│   └── sentiment_analyzer.py # AI sentiment scoring
├── utils/
│   ├── __init__.py
│   ├── logger.py           # Logging utilities
│   ├── helpers.py          # Common functions
│   └── cron_setup.py       # Cron job installer
├── data/
│   ├── input/              # Input CSV files
│   ├── output/             # Generated leads/results
│   └── logs/               # System logs
├── templates/
│   ├── voice_script.txt    # Twilio voice message
│   ├── telegram_message.txt # Telegram template
│   └── whatsapp_template.txt # WhatsApp template
├── install.sh              # Termux installation script
└── README.md              # Complete documentation
```

## 🚀 Quick Setup Commands

### 1. Initial Setup
```bash
# Clone/create project directory
mkdir -p termux_outreach_ai
cd termux_outreach_ai

# Run installation script
chmod +x install.sh
./install.sh
```

### 2. Configuration
```bash
# Copy and edit environment variables
cp config/.env.template config/.env
nano config/.env

# Test individual modules
python modules/twilio_dialer.py --test
python modules/telegram_bot.py --test
```

### 3. Daily Automation
```bash
# Install cron job
python utils/cron_setup.py --install

# Manual run
python main.py --mode=full

# Test run (no actual API calls)
python main.py --mode=test
```

## 📋 Required API Keys & Services

### Essential Services
- **Twilio**: Voice API for auto-dialing
- **Telegram Bot**: Bot token from @BotFather
- **WhatsApp Business API**: Cloud API or Business Account
- **Optional**: OpenAI API for advanced sentiment analysis

### Free Alternatives
- **Twilio**: Free trial with $15 credit
- **Telegram**: Completely free
- **WhatsApp**: Free tier available
- **Sentiment Analysis**: Local GPT4All model (offline)

## 🔧 Module Dependencies

### Core Python Packages
```bash
pip install requests beautifulsoup4 pandas numpy
pip install twilio telegram-bot-api selenium
pip install nltk textblob pyrogram
```

### Termux-Specific Packages
```bash
pkg install curl jq python nodejs
pkg install chromium-browser # For web automation
pkg install cronie # For cron jobs
```

## 🎯 Usage Examples

### Individual Module Testing
```bash
# Test voice dialer
python modules/twilio_dialer.py --phone="+60123456789" --test

# Test Telegram bot
python modules/telegram_bot.py --username="@restaurant_owner" --test

# Test social scraper
python modules/social_scraper.py --url="facebook.com/restaurant" --test
```

### Full System Run
```bash
# Production run
python main.py --mode=production --input=data/input/leads.csv

# Test mode (no API calls)
python main.py --mode=test --input=data/input/sample_leads.csv

# Specific modules only
python main.py --modules=twilio,telegram --input=data/input/hot_leads.csv
```

This structure provides complete modularity, easy testing, and production-ready deployment for Termux environments.
