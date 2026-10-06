"""
translator.py
Multilingual Translation Support Module for OurScheme.

Supported Languages:
- en: English
- hi: हिन्दी (Hindi)
- mr: मराठी (Marathi)
- bn: বাংলা (Bengali)
- gu: ગુજરાતી (Gujarati)
- ta: தமிழ் (Tamil)
- te: తెలుగు (Telugu)
- kn: ಕನ್ನಡ (Kannada)
- pa: ਪੰਜਾਬੀ (Punjabi)
- ml: മലയാളം (Malayalam)
"""

import os

SUPPORTED_LANGUAGES = {
    "en": {"name": "English", "native": "English"},
    "hi": {"name": "Hindi", "native": "हिन्दी"},
    "mr": {"name": "Marathi", "native": "मराठी"},
    "bn": {"name": "Bengali", "native": "বাংলা"},
    "gu": {"name": "Gujarati", "native": "ગુજરાતી"},
    "ta": {"name": "Tamil", "native": "தமிழ்"},
    "te": {"name": "Telugu", "native": "తెలుగు"},
    "kn": {"name": "Kannada", "native": "ಕನ್ನಡ"},
    "pa": {"name": "Punjabi", "native": "ਪੰਜਾਬੀ"},
    "ml": {"name": "Malayalam", "native": "മലയാളം"}
}

def get_language_name(code):
    """Returns the native display name for a language code."""
    lang = SUPPORTED_LANGUAGES.get(code)
    if lang:
        return f"{lang['native']} ({lang['name']})" if code != "en" else "English"
    return "English"

def translate_text_backend(text, target_lang="hi"):
    """
    Backend translation helper using Google GenAI API if GEMINI_API_KEY is configured.
    For frontend full-page translation, the Google Translate Element API handles it dynamically.
    """
    if not text or target_lang == "en":
        return text

    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if api_key:
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            target_name = SUPPORTED_LANGUAGES.get(target_lang, {}).get("name", "Hindi")
            prompt = f"Translate the following government scheme information into {target_name}. Return ONLY the direct translation:\n\n{text}"
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            return response.text.strip()
        except Exception:
            return text
    return text
