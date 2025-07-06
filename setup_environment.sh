#setup_environment.sh
#!/bin/bash
pkg update && pkg upgrade -y
pkg install python python-pip curl jq gawk git -y
pip install pandas pyrogram requests python-dotenv schedule

mkdir -p voice_messages logs
touch automation.log

echo "TELEGRAM_API_ID=your_api_id" > .env
echo "TELEGRAM_API_HASH=your_api_hash" >> .env
echo "TELEGRAM_BOT_TOKEN=your_bot_token" >> .env
echo "ELEVENLABS_API_KEY=your_elevenlabs_key" >> .env
echo "ELEVENLABS_VOICE_ID=EXAVITQu4vr4xnSDxMaL" >> .env

chmod +x get_malaysia_venues.sh
chmod +x setup_environment.sh

echo "Environment setup complete"