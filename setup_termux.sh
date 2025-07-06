!/bin/bash
# Termux setup script for outreach system

echo "🔧 Setting up Termux environment..."

# Update packages
pkg update && pkg upgrade -y

# Install Python and essential tools
pkg install python python-pip git curl wget -y

# Install system dependencies
pkg install libxml2 libxslt libjpeg-turbo zlib -y

# Install Python packages
pip install -r requirements.txt

# Set up cron for automation
pkg install cronie -y

# Create cron job for daily execution
(crontab -l 2>/dev/null; echo "0 9 * * * cd /data/data/com.termux/files/home/outreach_system && python main.py") | crontab -

# Create data directories
mkdir -p data output logs

# Set permissions
chmod +x main.py
chmod +x setup_termux.sh

echo "✅ Termux setup complete!"
echo "📝 Next steps:"
echo "1. Copy .env.template to .env and add your API keys"
echo "2. Add venue data to data/venues.csv"
echo "3. Add Telegram targets to data/telegram_targets.csv"
echo "4. Add websites to data/websites.csv"
echo "5. Run: python main.py"