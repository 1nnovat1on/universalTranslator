# flask_app.py
import speech_recognition as sr
from googletrans import Translator
# Consider gTTS or other libraries if you want server-side audio generation later
# import pyttsx3 # We won't use pyttsx3 for speaking directly anymore
from langdetect import detect
from flask import Flask, request, jsonify
from flask_cors import CORS # Needed for requests from Squarespace
import io
import os
from pydub import AudioSegment # To handle audio format conversion

# --- Initialization ---
app = Flask(__name__)
# IMPORTANT: Configure CORS properly for your Squarespace domain in production
# For development, '*' might be okay, but restrict it later.
CORS(app)

r = sr.Recognizer()
translator = Translator()

# --- Helper Function (Optional but Recommended) ---
def get_supported_languages():
    # googletrans doesn't have a built-in list readily available in the same way
    # as some other libraries. You might need to hardcode a list based on
    # common languages or the ones googletrans generally supports.
    # Example:
    return {
        'en': 'English',
        'es': 'Spanish',
        'fr': 'French',
        'de': 'German',
        'ja': 'Japanese',
        'ko': 'Korean',
        'zh-cn': 'Chinese (Simplified)'
        # Add more as needed
    }

# --- API Endpoints ---
@app.route('/api/languages', methods=['GET'])
def languages():
    """Returns a list of supported languages for the dropdowns."""
    return jsonify(get_supported_languages())

@app.route('/api/translate', methods=['POST'])
def translate_speech():
    """
    Receives audio, performs STT, translation, and returns text.
    """
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file part"}), 400
    if 'targetLang' not in request.form:
        return jsonify({"error": "Missing target language"}), 400
    # sourceLang might be 'auto' or a specific code from frontend
    source_lang_code = request.form.get('sourceLang', 'auto')
    target_lang_code = request.form['targetLang']

    audio_file = request.files['audio']

    try:
        # --- Audio Processing ---
        # Browsers often send webm or ogg. speech_recognition needs WAV.
        # Use pydub to convert. You might need ffmpeg installed on your server.
        audio_data = io.BytesIO(audio_file.read())
        # Determine format if possible (safer to assume webm/ogg from browser)
        # Use 'audio_file.filename' or 'audio_file.content_type' if provided by browser
        # Forcing format might be needed:
        sound = AudioSegment.from_file(audio_data) # pydub attempts auto-detect
        # Or specify format: sound = AudioSegment.from_file(audio_data, format="webm")

        wav_data = io.BytesIO()
        sound.export(wav_data, format="wav")
        wav_data.seek(0) # Rewind buffer

        # --- Speech Recognition ---
        with sr.AudioFile(wav_data) as source:
            # r.adjust_for_ambient_noise(source) # Less applicable for short uploads
            audio = r.record(source) # Read the entire audio file

        # Use recognize_google, specifying language if provided and not 'auto'
        if source_lang_code != 'auto':
             recognized_text = r.recognize_google(audio, language=source_lang_code)
        else:
             recognized_text = r.recognize_google(audio) # Let Google auto-detect

        print(f"Recognized: {recognized_text}")

        # --- Language Detection (Optional confirmation/refinement) ---
        try:
            detected_lang = detect(recognized_text)
            print(f"Detected Language: {detected_lang}")
            # If source was auto, you could use detected_lang now, but
            # googletrans often works fine with src='auto' too.
            # If detected_lang == target_lang_code, maybe skip translation?
            if detected_lang == target_lang_code:
                 print("Detected language is the same as target. No translation needed.")
                 # Decide if you want to return the original or an empty translation
                 return jsonify({
                     "original": recognized_text,
                     "translated": recognized_text, # Or ""
                     "detected_lang": detected_lang
                 })

        except Exception as detect_err:
            print(f"Language detection failed: {detect_err}")
            detected_lang = source_lang_code # Fallback

        # --- Translation ---
        # Let googletrans auto-detect source if 'auto' was chosen
        trans_src = source_lang_code if source_lang_code != 'auto' else 'auto'
        translated_obj = translator.translate(recognized_text, dest=target_lang_code, src=trans_src)
        translated_text = translated_obj.text

        print(f"Translated ({target_lang_code}): {translated_text}")

        # --- Response ---
        return jsonify({
            "original": recognized_text,
            "translated": translated_text,
            "detected_lang": detected_lang if 'detected_lang' in locals() else trans_src # report detected lang
        })

    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
        return jsonify({"error": "Could not understand audio"}), 400
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        return jsonify({"error": f"Speech recognition service error: {e}"}), 500
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc() # Print detailed error for debugging
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500

# --- Run the App (for local development) ---
if __name__ == '__main__':
    # Remember to install required libraries:
    # pip install Flask Flask-Cors SpeechRecognition googletrans langdetect pydub
    # You might also need to install ffmpeg for pydub: https://github.com/jiaaro/pydub#installation
    app.run(debug=True, port=5000) # Run on port 5000 locally