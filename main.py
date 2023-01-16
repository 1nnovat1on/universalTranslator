# Built for Windows which is by far the most used and accessible operating system, don't kid yourself now.
# ABSTERGO LLC | COLIN JACKSON | 1-16-2023
import speech_recognition as sr
from googletrans import Translator
import json
import pyttsx3
from langdetect import detect

AWAKE = True

# Initialize recognizer class (for recognizing the speech)
r = sr.Recognizer()

# Initialize the translator
translator = Translator()

# Get the language code for the language to which you want to translate
target_language = 'fr'

# Get the language code for the language from which you are translating
source_language = 'en'

global engine
global counter
counter = 0



def listen():
    
    while AWAKE:
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source)
            audio_data = r.listen(source)
            try:
                text = r.recognize_google(audio_data)
                lang = detect(text)
                print(f"Recognized: {text}")
                print(f"Language: {lang}")

                if lang == target_language:
                    print(f"source language detected: {target_language}")
                    return ''

                return text

            except Exception as e:
                continue

def talk(text = None):
    
    global counter
    global engine
    
    if counter == 0:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[1].id)
        counter = counter + 1
    
    engine.say(text)
    engine.runAndWait()

def translate(text = None):
    translated_text = translator.translate(text, dest=target_language, src='en')
    print(f"Original: {text}")
    print(f"Translated ({target_language}): {translated_text.text}")

    textToSay = translated_text.text

    return textToSay

def main():

    while AWAKE:
        try:

            text = listen()

            if text is None:
                continue

            elif text == '' or text == '...' or text == ' ':
                continue

            translated_text = translator.translate(text, dest=target_language, src='en')
            print(f"Original: {text}")
            
            print(f"Translated ({target_language}): {translated_text.text}")

            textToSay = translated_text.text
            talk(textToSay)

        except sr.UnknownValueError:
            print("Could not understand audio")
        except sr.RequestError as e:
            print("Error: {0}".format(e))


# helper functions
# you must have the voice text-to-speech module for your target language installed to hear correct pronunciation

# detects available voices in Windows
def getVoices():

    engine = pyttsx3.init()

    for voice in engine.getProperty('voices'):
        print(voice)

main()
#getVoices()
