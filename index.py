import requests
import webcolors

def translate_color_name(color_name, from_lang='ru', to_lang='en'):
    """Translate color names using the LibreTranslate API."""
    url = "https://libretranslate.com/translate"
    payload = {
        "q": color_name,
        "source": from_lang,
        "target": to_lang,
        "format": "text"
    }
    headers = {
        "Content-Type": "application/json",
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json().get('translatedText')
    else:
        print("Error during translation")
        return None

def get_hex_color_by_name(color_name):
    """Convert a color name to a hex code."""
    try:
        return webcolors.name_to_hex(color_name)
    except Exception as e:
        print(f"Error finding color: {e}")
        return "Color name not found"

def get_color_code_by_russian_name(russian_color_name):
    """Translate a Russian color name to English and get its hex code."""
    english_color_name = translate_color_name(russian_color_name)
    if english_color_name:
        return get_hex_color_by_name(english_color_name)
    return "Unable to find or translate color."

# Example usage
print(get_color_code_by_russian_name("синий"))  # Should print the hex code for blue, e.g., "#0000FF"
