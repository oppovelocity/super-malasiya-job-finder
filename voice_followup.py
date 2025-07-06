#voice_followup.py
import os
import csv
import requests
from datetime import datetime

class VoiceFollowup:
    def __init__(self):
        self.elevenlabs_key = os.getenv('ELEVENLABS_API_KEY')
        self.voice_id = os.getenv('ELEVENLABS_VOICE_ID', 'EXAVITQu4vr4xnSDxMaL')
        
    def generate_voice_message(self, venue_name):
        text = f"Hello, this is Sarah from HireBot. I noticed {venue_name} might be hiring. I can help streamline your recruitment process and save you time. Please call back if interested."
        
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"
        headers = {
            'Accept': 'audio/mpeg',
            'Content-Type': 'application/json',
            'xi-api-key': self.elevenlabs_key
        }
        
        data = {
            'text': text,
            'model_id': 'eleven_monolingual_v1',
            'voice_settings': {
                'stability': 0.5,
                'similarity_boost': 0.5
            }
        }
        
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            filename = f"voice_messages/{venue_name.replace(' ', '_')}.mp3"
            os.makedirs('voice_messages', exist_ok=True)
            with open(filename, 'wb') as f:
                f.write(response.content)
            return filename
        return None
    
    def process_leads(self):
        results = []
        
        with open('hiring_leads.csv', 'r') as f:
            reader = csv.DictReader(f)
            for lead in reader:
                if lead['hiring_score'] and int(lead['hiring_score']) > 1:
                    voice_file = self.generate_voice_message(lead['name'])
                    results.append({
                        'name': lead['name'],
                        'phone': lead['phone'],
                        'voice_file': voice_file,
                        'generated_at': datetime.now().isoformat()
                    })
        
        with open('voice_followups.csv', 'w', newline='') as f:
            if results:
                writer = csv.DictWriter(f, fieldnames=results[0].keys())
                writer.writeheader()
                writer.writerows(results)
        
        return len(results)

if __name__ == "__main__":
    voice = VoiceFollowup()
    count = voice.process_leads()
    print(f"Generated {count} voice messages")