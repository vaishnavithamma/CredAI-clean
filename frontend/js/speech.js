let recognizer = null;
let isListening = false;
let onTranscriptCallback = null;
let noSpeechTimer = null;

const LANG_CODES = {
  'en': 'en-IN',
  'hi': 'hi-IN',
  'kn': 'kn-IN'
};

const SPEECH_SUPPORTED = !!(window.SpeechRecognition || window.webkitSpeechRecognition);

function initSpeechRecognition(lang) {
  if (!SPEECH_SUPPORTED) return null;
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  const rec = new SpeechRecognition();
  rec.lang = LANG_CODES[lang] || 'en-IN';
  rec.continuous = false;
  rec.interimResults = true;
  rec.maxAlternatives = 3;
  return rec;
}

function startListening(lang, callback) {
  onTranscriptCallback = callback;
  
  if (!SPEECH_SUPPORTED) {
    console.warn('Speech recognition not supported');
    document.getElementById('typed-fallback').style.display = 'block';
    return;
  }
  
  if (isListening) stopListening();
  
  recognizer = initSpeechRecognition(lang);
  
  recognizer.onstart = () => {
    isListening = true;
    document.getElementById('mic-waveform').style.display = 'flex';
    document.getElementById('interim-transcript-area').style.display = 'block';
    // Auto-timeout after 10 seconds of silence
    noSpeechTimer = setTimeout(() => { if (isListening) stopListening(); }, 10000);
  };
  
  recognizer.onresult = (event) => {
    clearTimeout(noSpeechTimer);
    let interimTranscript = '';
    let finalTranscript = '';
    for (let i = event.resultIndex; i < event.results.length; i++) {
      const transcript = event.results[i][0].transcript;
      if (event.results[i].isFinal) {
        finalTranscript += transcript;
      } else {
        interimTranscript += transcript;
      }
    }
    if (interimTranscript && callback) callback(interimTranscript, false);
    if (finalTranscript && callback) callback(finalTranscript, true);
  };
  
  recognizer.onerror = (event) => {
    console.error('Speech recognition error:', event.error);
    isListening = false;
    document.getElementById('mic-waveform').style.display = 'none';
    document.getElementById('interim-transcript-area').style.display = 'none';
    if (event.error === 'not-allowed') {
      document.getElementById('typed-fallback').style.display = 'block';
      assistant.appendAssistantMessage("Microphone access denied. Please type your answer.");
    } else if (event.error === 'no-speech') {
      if (callback) callback('', true); // triggers unclear answer handling
    }
  };
  
  recognizer.onend = () => {
    isListening = false;
    clearTimeout(noSpeechTimer);
    document.getElementById('mic-waveform').style.display = 'none';
    document.getElementById('interim-transcript-area').style.display = 'none';
  };
  
  try { recognizer.start(); } catch(e) { console.error('Failed to start recognizer:', e); }
}

function stopListening() {
  if (recognizer && isListening) {
    try { recognizer.stop(); } catch(e) {}
  }
  isListening = false;
  clearTimeout(noSpeechTimer);
  const waveform = document.getElementById('mic-waveform');
  if(waveform) waveform.style.display = 'none';
}

// TEXT TO SPEECH
// Async fix for voiceschanged
function getVoicesAsync() {
  return new Promise(resolve => {
    let voices = window.speechSynthesis.getVoices();
    if (voices.length > 0) {
      resolve(voices);
      return;
    }
    window.speechSynthesis.onvoiceschanged = () => {
      voices = window.speechSynthesis.getVoices();
      resolve(voices);
    };
  });
}

async function speakText(text, lang) {
  if (!window.speechSynthesis) return;
  window.speechSynthesis.cancel();
  
  const utterance = new SpeechSynthesisUtterance(text);
  const langCode = LANG_CODES[lang] || 'en-IN';
  utterance.lang = langCode;
  utterance.rate = 0.9;
  utterance.pitch = 1.05;
  utterance.volume = 1.0;
  
  const voices = await getVoicesAsync();
  let bestVoice = voices.find(v => v.lang === langCode);
  if (!bestVoice) bestVoice = voices.find(v => v.lang.startsWith(langCode.split('-')[0]));
  if (!bestVoice && lang === 'kn') bestVoice = voices.find(v => v.lang.startsWith('en')); // fallback
  if (bestVoice) utterance.voice = bestVoice;
  
  return new Promise((resolve) => {
    utterance.onend = () => resolve();
    utterance.onerror = () => resolve();
    window.speechSynthesis.speak(utterance);
    // Failsafe
    setTimeout(() => resolve(), text.length * 80 + 1000);
  });
}
