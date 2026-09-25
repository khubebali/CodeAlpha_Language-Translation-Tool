# app.py - Complete Python Backend with Flask
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import json
import logging
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Language codes mapping
LANGUAGES = {
    'en': 'English',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'it': 'Italian',
    'pt': 'Portuguese',
    'ru': 'Russian',
    'ja': 'Japanese',
    'ko': 'Korean',
    'zh': 'Chinese (Simplified)',
    'ar': 'Arabic',
    'hi': 'Hindi',
    'ur': 'Urdu'
}

@app.route('/')
def index():
    """Serve the main HTML page"""
    return render_template('index.html', languages=LANGUAGES)

@app.route('/api/translate', methods=['POST'])
def translate():
    """Translation API endpoint"""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        source = data.get('source', 'en')
        target = data.get('target', 'ur')
        
        if not text:
            return jsonify({
                'success': False,
                'error': 'No text provided for translation'
            }), 400
        
        logger.info(f"Translating: '{text[:50]}...' from {source} to {target}")
        
        # Try MyMemory API first (free, no key required)
        try:
            translated = translate_with_mymemory(text, source, target)
            logger.info("Translation successful with MyMemory")
            return jsonify({
                'success': True,
                'translated_text': translated,
                'source': source,
                'target': target,
                'service': 'MyMemory'
            })
        except Exception as e:
            logger.warning(f"MyMemory failed: {str(e)}")
            
            # Fallback to LibreTranslate
            try:
                translated = translate_with_libre(text, source, target)
                logger.info("Translation successful with LibreTranslate")
                return jsonify({
                    'success': True,
                    'translated_text': translated,
                    'source': source,
                    'target': target,
                    'service': 'LibreTranslate'
                })
            except Exception as e2:
                logger.warning(f"LibreTranslate failed: {str(e2)}")
                
                # Final fallback: Simulate translation for demo
                translated = simulate_translation(text, source, target)
                logger.info("Using simulated translation")
                return jsonify({
                    'success': True,
                    'translated_text': translated,
                    'source': source,
                    'target': target,
                    'service': 'Simulated (Fallback)'
                })
                
    except Exception as e:
        logger.error(f"Translation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Translation failed: {str(e)}'
        }), 500

def translate_with_mymemory(text, source, target):
    """Translate using MyMemory API"""
    url = f"https://api.mymemory.translated.net/get"
    params = {
        'q': text,
        'langpair': f"{source}|{target}",
        'de': 'demo@example.com'
    }
    
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    
    data = response.json()
    if data.get('responseStatus') == 200 and data.get('responseData'):
        return data['responseData']['translatedText']
    else:
        error_msg = data.get('responseDetails', 'Unknown error')
        raise Exception(f"MyMemory error: {error_msg}")

def translate_with_libre(text, source, target):
    """Translate using LibreTranslate API"""
    url = "https://libretranslate.com/translate"
    payload = {
        'q': text,
        'source': source,
        'target': target,
        'format': 'text'
    }
    
    response = requests.post(url, json=payload, timeout=10)
    response.raise_for_status()
    
    data = response.json()
    if 'translatedText' in data:
        return data['translatedText']
    else:
        raise Exception("LibreTranslate returned unexpected response")

def simulate_translation(text, source, target):
    """Simulate translation for demo purposes"""
    # Simple mock translation for common phrases
    mock_translations = {
        ('en', 'ur'): {
            'hello': 'ہیلو',
            'how are you': 'آپ کیسے ہیں',
            'good morning': 'صبح بخیر',
            'good night': 'شب بخیر',
            'thank you': 'شکریہ',
            'welcome': 'خوش آمدید',
            'yes': 'جی ہاں',
            'no': 'نہیں',
            'please': 'براہ کرم',
            'sorry': 'معاف کیجیے',
            'i love you': 'میں آپ سے محبت کرتا ہوں',
            'what is your name': 'آپ کا نام کیا ہے',
            'my name is': 'میرا نام ہے',
            'where are you from': 'آپ کہاں سے ہیں',
            'i am from': 'میں سے ہوں',
            'how old are you': 'آپ کی عمر کیا ہے',
            'i am': 'میں ہوں',
            'good': 'اچھا',
            'bad': 'برا',
            'beautiful': 'خوبصورت',
            'excellent': 'بہترین',
        },
        ('ur', 'en'): {
            'ہیلو': 'Hello',
            'آپ کیسے ہیں': 'How are you',
            'صبح بخیر': 'Good morning',
            'شب بخیر': 'Good night',
            'شکریہ': 'Thank you',
            'خوش آمدید': 'Welcome',
            'جی ہاں': 'Yes',
            'نہیں': 'No',
            'براہ کرم': 'Please',
            'معاف کیجیے': 'Sorry',
            'میں آپ سے محبت کرتا ہوں': 'I love you',
            'آپ کا نام کیا ہے': 'What is your name',
            'میرا نام ہے': 'My name is',
            'آپ کہاں سے ہیں': 'Where are you from',
            'میں سے ہوں': 'I am from',
            'آپ کی عمر کیا ہے': 'How old are you',
            'میں ہوں': 'I am',
            'اچھا': 'Good',
            'برا': 'Bad',
            'خوبصورت': 'Beautiful',
            'بہترین': 'Excellent',
        }
    }
    
    text_lower = text.lower()
    mock_key = (source, target)
    
    if mock_key in mock_translations:
        for phrase, translation in mock_translations[mock_key].items():
            if phrase in text_lower:
                return text.replace(phrase, translation, 1)
    
    # Generic mock translation
    return f"[{LANGUAGES.get(source, source)} → {LANGUAGES.get(target, target)}] {text}"

@app.route('/api/languages', methods=['GET'])
def get_languages():
    """Get list of supported languages"""
    return jsonify(LANGUAGES)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'languages': len(LANGUAGES)
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)