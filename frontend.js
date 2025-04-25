// src/App.js (Example structure)
import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios'; // npm install axios
import './App.css';

// IMPORTANT: Replace with the actual URL of your deployed Flask app
const API_BASE_URL = 'http://localhost:5000'; // For local dev
// const API_BASE_URL = 'https://your-flask-app-url.com'; // For production

function App() {
  const [sourceLang, setSourceLang] = useState('en'); // Default source
  const [targetLang, setTargetLang] = useState('fr'); // Default target
  const [supportedLangs, setSupportedLangs] = useState({}); // Store languages from backend

  const [isRecording, setIsRecording] = useState(false);
  const [originalText, setOriginalText] = useState('');
  const [translatedText, setTranslatedText] = useState('');
  const [statusMessage, setStatusMessage] = useState('Select languages and press Record');
  const [error, setError] = useState('');

  const mediaRecorder = useRef(null);
  const audioChunks = useRef([]);

  // Fetch supported languages on component mount
  useEffect(() => {
    axios.get(`${API_BASE_URL}/api/languages`)
      .then(response => {
        setSupportedLangs(response.data);
        // Optionally set defaults based on fetched langs if needed
      })
      .catch(err => {
        console.error("Error fetching languages:", err);
        setError('Could not load languages from server.');
        // Provide some defaults maybe?
        setSupportedLangs({ 'en': 'English', 'fr': 'French', 'es': 'Spanish', 'de': 'German'});
      });
  }, []);


  const startRecording = async () => {
    setError('');
    setOriginalText('');
    setTranslatedText('');
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder.current = new MediaRecorder(stream);
      audioChunks.current = []; // Reset chunks

      mediaRecorder.current.ondataavailable = event => {
        audioChunks.current.push(event.data);
      };

      mediaRecorder.current.onstop = async () => {
        setStatusMessage('Processing...');
        const audioBlob = new Blob(audioChunks.current, { type: 'audio/webm' }); // or 'audio/ogg' depending on browser

        const formData = new FormData();
        formData.append('audio', audioBlob, 'recording.webm'); // Filename helps server identify
        formData.append('sourceLang', sourceLang);
        formData.append('targetLang', targetLang);

        try {
          const response = await axios.post(`${API_BASE_URL}/api/translate`, formData, {
            headers: {
              'Content-Type': 'multipart/form-data',
            },
          });
          setOriginalText(response.data.original);
          setTranslatedText(response.data.translated);
          setStatusMessage('Translation complete. Press Record to start again.');
          speakText(response.data.translated); // Speak the result
        } catch (err) {
          console.error("Error uploading/translating:", err);
          const errorMsg = err.response?.data?.error || 'Failed to translate. Check server logs.';
          setError(`Translation Error: ${errorMsg}`);
          setStatusMessage('Error occurred. Try again.');
        } finally {
             // Clean up the stream tracks
             stream.getTracks().forEach(track => track.stop());
        }
      };

      mediaRecorder.current.start();
      setIsRecording(true);
      setStatusMessage('Recording... Press Stop when finished.');

    } catch (err) {
      console.error("Error accessing microphone:", err);
      setError('Could not access microphone. Please grant permission.');
      setStatusMessage('Microphone access denied.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorder.current && isRecording) {
      mediaRecorder.current.stop();
      setIsRecording(false);
      // Processing starts in onstop handler
    }
  };

  const speakText = (text) => {
    if ('speechSynthesis' in window && text) {
      const utterance = new SpeechSynthesisUtterance(text);
       // Try to set the voice based on the target language
      utterance.lang = targetLang; // Sets the language for pronunciation

      // Optional: Find a specific voice for the language if available
      const voices = window.speechSynthesis.getVoices();
      const targetVoice = voices.find(voice => voice.lang.startsWith(targetLang));
      if (targetVoice) {
         utterance.voice = targetVoice;
         console.log(`Using voice: ${targetVoice.name} for lang: ${targetLang}`);
      } else {
         console.warn(`No specific voice found for language ${targetLang}. Using default.`);
      }


      window.speechSynthesis.cancel(); // Cancel any previous speech
      window.speechSynthesis.speak(utterance);
    } else {
       console.warn("Speech synthesis not supported or no text to speak.");
    }
  };

   // Need to load voices async sometimes, especially on first load
   useEffect(() => {
    if ('speechSynthesis' in window) {
        window.speechSynthesis.onvoiceschanged = () => {
            // Pre-load voices if needed, or just ensure they are loaded before first speak attempt
            console.log("Voices loaded:", window.speechSynthesis.getVoices().length);
        };
    }
   }, []);


  return (
    <div className="App">
      <h1>Real-time Translator</h1>

      <div className="controls">
        <label>
          Input Language:
          <select value={sourceLang} onChange={e => setSourceLang(e.target.value)}>
            {/* Add an 'auto' option */}
            <option value="auto">Auto-Detect</option>
            {Object.entries(supportedLangs).map(([code, name]) => (
              <option key={code} value={code}>{name}</option>
            ))}
          </select>
        </label>

        <label>
          Output Language:
          <select value={targetLang} onChange={e => setTargetLang(e.target.value)}>
            {Object.entries(supportedLangs).map(([code, name]) => (
              <option key={code} value={code}>{name}</option>
            ))}
          </select>
        </label>

        <button onClick={isRecording ? stopRecording : startRecording} disabled={!supportedLangs}>
          {isRecording ? 'Stop Recording' : 'Record'}
        </button>
      </div>

      <div className="status">
        {statusMessage}
      </div>

      {error && <div className="error">{error}</div>}

      <div className="results">
        {originalText && (
          <div className="text-section">
            <h2>Original:</h2>
            <p>{originalText}</p>
          </div>
        )}
        {translatedText && (
          <div className="text-section">
            <h2>Translated ({targetLang}):</h2>
            <p>{translatedText}</p>
            {/* Optional: Add a button to replay the speech */}
            <button onClick={() => speakText(translatedText)} disabled={!('speechSynthesis' in window)}>
              Speak Again
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;