const AssistantState = {
  IDLE: 'idle',
  SPEAKING: 'speaking',
  LISTENING: 'listening',
  PROCESSING: 'processing',
  CONFIRMING: 'confirming',
  COMPLETE: 'complete'
};

class CredAIAssistant {
  constructor() {
    this.language = 'en';
    this.fields = [];
    this.answers = {};
    this.state = AssistantState.IDLE;
    this.currentField = null;
    this.retryCount = 0;
    this.MAX_RETRIES = 2; // Trigger graceful fallback on 2nd failure
    this.sessionId = null;
    this.pdfFile = null;
  }

  selectLanguage(lang) {
    this.language = lang;
    document.querySelectorAll('.lang-pill').forEach(p => p.classList.remove('selected'));
    const selected = document.querySelector(`[data-lang="${lang}"]`);
    if(selected) selected.classList.add('selected');
    
    const greetings = {
      'en': "Hello! I'm your AI loan assistant. I will ask you a few questions to fill your loan application. Please answer by speaking or typing. Let's begin!",
      'hi': "नमस्ते! मैं आपका AI ऋण सहायक हूँ। मैं आपसे कुछ सवाल पूछूंगा ताकि आपका ऋण आवेदन भरा जा सके। बोलकर या लिखकर जवाब दें। चलिए शुरू करते हैं!",
      'kn': "ನಮಸ್ಕಾರ! ನಾನು ನಿಮ್ಮ AI ಸಾಲ ಸಹಾಯಕ. ನಿಮ್ಮ ಸಾಲ ಅರ್ಜಿ ತುಂಬಲು ಕೆಲವು ಪ್ರಶ್ನೆಗಳನ್ನು ಕೇಳುತ್ತೇನೆ. ಮಾತನಾಡಿ ಅಥವಾ ಟೈಪ್ ಮಾಡಿ ಉತ್ತರಿಸಿ. ಪ್ರಾರಂಭಿಸೋಣ!"
    };
    this.appendAssistantMessage(greetings[lang]);
  }

  async initFields() {
    if (this.pdfFile) {
        this.appendAssistantMessage("Scanning your PDF document...");
        this.fields = await parsePDF(this.pdfFile);
    } else {
        this.fields = DEFAULT_LOAN_FIELDS;
    }
    this.answers = {};
    this.renderFieldChecklist();
    this.renderFormPreview();
    this.updateProgress();
  }

  async startInterview() {
    if (!this.language) {
      this.appendAssistantMessage("Please select a language first!");
      return;
    }
    document.getElementById('start-btn').disabled = true;
    
    if (this.fields.length === 0) {
      await this.initFields();
    }
    
    this.setState(AssistantState.SPEAKING);
    await this.askNextQuestion();
  }

  async askNextQuestion() {
    this.setState(AssistantState.PROCESSING);
    document.getElementById('typed-fallback').style.display = 'none'; // Hide typed input if showing
    
    try {
      const result = await fetch('/api/assistant/next-question', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            language: this.language,
            fields: this.fields,
            answers: this.answers
        })
      }).then(r => r.json());

      if (result.completed) {
        await this.handleCompletion();
        return;
      }

      this.currentField = result;
      this.updateCurrentQuestionCard(result.label, result.question_text);
      this.updateProgress(result.progress);
      this.highlightCurrentField(result.field_key);

      this.setState(AssistantState.SPEAKING);
      this.appendAssistantMessage(result.question_text);
      await speakText(result.question_text, this.language);

      this.setState(AssistantState.LISTENING);
      this.retryCount = 0;
      startListening(this.language, this.handleVoiceTranscript.bind(this));

    } catch (err) {
      console.error('Error getting next question:', err);
      this.appendAssistantMessage("Sorry, there was an error. Please check your connection.");
    }
  }

  async handleVoiceTranscript(transcript, isFinal) {
    if (!isFinal) {
      document.getElementById('interim-text').textContent = transcript;
      document.getElementById('interim-transcript-area').style.display = 'block';
      return;
    }
    
    document.getElementById('interim-transcript-area').style.display = 'none';
    document.getElementById('interim-text').textContent = '';
    
    if (!transcript || transcript.trim().length < 1) {
      this.handleUnclearAnswer();
      return;
    }

    this.appendUserMessage(transcript);
    await this.processAnswer(transcript);
  }

  async processAnswer(rawAnswer) {
    this.setState(AssistantState.PROCESSING);
    stopListening();
    
    const skipWords = ['skip', 'next', 'छोड़ो', 'अगला', 'ಬಿಡು', 'ಮುಂದೆ'];
    if (skipWords.some(w => rawAnswer.toLowerCase().includes(w))) {
      this.answers[this.currentField.field_key] = null;
      await this.askNextQuestion();
      return;
    }

    try {
      const result = await fetch('/api/assistant/map-answer', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            field_key: this.currentField.field_key,
            raw_answer: rawAnswer,
            language: this.language,
            field_type: this.currentField.type
        })
      }).then(r => r.json());

      if (result.needs_confirmation) {
        this.setState(AssistantState.CONFIRMING);
        await speakText(result.confirmation_question, this.language);
        this.appendAssistantMessage(result.confirmation_question);
        startListening(this.language, async (confirmText, isFinal) => {
          if (!isFinal) return;
          const yesWords = ['yes', 'correct', 'right', 'हाँ', 'हां', 'ಹೌದು', 'sari', 'ha'];
          if (yesWords.some(w => confirmText.toLowerCase().includes(w))) {
            this.fillField(result);
            await this.askNextQuestion();
          } else {
            await speakText("Let me ask again.", this.language);
            await this.askNextQuestion();
          }
        });
      } else {
        this.fillField(result);
        const ackMessages = { 'en': "Got it!", 'hi': "ठीक है!", 'kn': "ಸರಿ!" };
        this.appendAssistantMessage(ackMessages[this.language]);
        await this.askNextQuestion();
      }
    } catch (err) {
      console.error('Map answer error:', err);
      this.handleUnclearAnswer();
    }
  }

  fillField(result) {
    this.answers[result.field_key] = result.normalized_value;
    
    const fieldEl = document.getElementById(`field-preview-${result.field_key}`);
    if (fieldEl) {
      const valueEl = fieldEl.querySelector('.field-value');
      if (valueEl) {
        valueEl.textContent = result.display_value || result.normalized_value;
        fieldEl.classList.add('field-filled');
        setTimeout(() => fieldEl.classList.remove('field-filled'), 600);
      }
    }
    
    const checkItem = document.getElementById(`check-${result.field_key}`);
    if (checkItem) {
      checkItem.classList.remove('pending', 'current');
      checkItem.classList.add('completed');
      checkItem.querySelector('.status-icon').textContent = '✓';
    }
  }

  async handleUnclearAnswer() {
    this.retryCount++;
    if (this.retryCount >= this.MAX_RETRIES) {
      // Graceful fallback for Kannada/Hindi/English
      const fallbackMsg = {
        'en': "I'm having trouble understanding. Please type your answer.",
        'hi': "मुझे समझने में कठिनाई हो रही है। कृपया अपना उत्तर टाइप करें।",
        'kn': "ಅರ್ಥ ಮಾಡಿಕೊಳ್ಳಲು ತೊಂದರೆ ಆಗುತ್ತಿದೆ. ದಯವಿಟ್ಟು ಟೈಪ್ ಮಾಡಿ।"
      };
      this.appendAssistantMessage(fallbackMsg[this.language]);
      document.getElementById('typed-fallback').style.display = 'flex';
      return;
    }
    
    const repeatMsg = {
      'en': `Sorry, I didn't catch that. Could you please repeat?`,
      'hi': "माफ़ करें, मुझे सुनाई नहीं दिया। कृपया दोबारा बोलें।",
      'kn': "ಕ್ಷಮಿಸಿ, ಕೇಳಿಸಲಿಲ್ಲ. ದಯವಿಟ್ಟು ಮತ್ತೆ ಹೇಳಿ।"
    };
    await speakText(repeatMsg[this.language], this.language);
    this.appendAssistantMessage(repeatMsg[this.language]);
    startListening(this.language, this.handleVoiceTranscript.bind(this));
  }

  async handleCompletion() {
    this.setState(AssistantState.COMPLETE);
    const completeMsg = {
      'en': "Excellent! All questions answered. Let me review your application now.",
      'hi': "शाबाश! सभी सवालों के जवाब मिल गए। अब मैं आपका आवेदन जाँचता हूँ।",
      'kn': "ಅದ್ಭುತ! ಎಲ್ಲಾ ಪ್ರಶ್ನೆಗಳಿಗೆ ಉತ್ತರಿಸಿದ್ದೀರಿ. ಈಗ ನಿಮ್ಮ ಅರ್ಜಿ ಪರಿಶೀಲಿಸುತ್ತೇನೆ।"
    };
    await speakText(completeMsg[this.language], this.language);
    this.appendAssistantMessage(completeMsg[this.language]);
    document.getElementById('submit-section').style.display = 'block';
    document.getElementById('submit-section').scrollIntoView({ behavior: 'smooth' });
  }

  appendAssistantMessage(text) {
    const chat = document.getElementById('chat-container');
    const bubble = document.createElement('div');
    bubble.className = 'bubble-ai';
    bubble.innerHTML = `<p style="font-size:0.875rem;color:rgba(255,255,255,0.9);">${text}</p>`;
    chat.appendChild(bubble);
    chat.scrollTop = chat.scrollHeight;
    
    if (this.state === AssistantState.SPEAKING) {
      const avatar = document.getElementById('assistant-avatar');
      if (avatar) {
        avatar.parentElement.classList.add('ai-speaking');
        setTimeout(() => {
          avatar.parentElement.classList.remove('ai-speaking');
        }, 2000);
      }
    }
  }

  appendUserMessage(text) {
    const chat = document.getElementById('chat-container');
    const bubble = document.createElement('div');
    bubble.className = 'bubble-user';
    bubble.innerHTML = `<p style="font-size:0.875rem;color:rgba(255,255,255,0.9);">${text}</p>`;
    chat.appendChild(bubble);
    chat.scrollTop = chat.scrollHeight;
  }

  setState(newState) {
    this.state = newState;
    const statusEl = document.getElementById('assistant-status');
    const micBtn = document.getElementById('mic-btn');
    const waveform = document.getElementById('mic-waveform');
    
    const statusLabels = {
      [AssistantState.IDLE]: 'Ready to help',
      [AssistantState.SPEAKING]: '🔊 Speaking...',
      [AssistantState.LISTENING]: '🎤 Listening...',
      [AssistantState.PROCESSING]: '⚙️ Processing...',
      [AssistantState.CONFIRMING]: '🤔 Confirming...',
      [AssistantState.COMPLETE]: '✅ All done!'
    };
    if (statusEl) statusEl.textContent = statusLabels[newState] || '';
    
    if (newState === AssistantState.LISTENING) {
      micBtn?.classList.add('listening');
      if (waveform) waveform.style.display = 'flex';
    } else {
      micBtn?.classList.remove('listening');
      if (waveform) waveform.style.display = 'none';
    }
  }

  updateCurrentQuestionCard(label, question) {
    const lbl = document.getElementById('current-field-label');
    const qEl = document.getElementById('current-question-text');
    const card = document.getElementById('current-question-card');
    if(lbl) lbl.textContent = label;
    if(qEl) qEl.textContent = question;
    if(card) card.style.display = 'block';
  }

  updateProgress(progress) {
    if (!progress) return;
    const pct = progress.percent || 0;
    document.getElementById('progress-percent').textContent = `${pct}%`;
    document.getElementById('progress-bar-fill').style.width = `${pct}%`;
  }

  renderFieldChecklist() {
    const container = document.getElementById('field-checklist');
    if (!container) return;
    container.innerHTML = '';
    this.fields.filter(f => f.required).forEach(f => {
      const item = document.createElement('div');
      item.id = `check-${f.field_key}`;
      item.className = 'field-status-item pending';
      item.style.cssText = 'display:flex;align-items:center;gap:8px;padding:4px 6px;border-radius:6px;transition:all 0.3s;';
      item.innerHTML = `<span class="status-icon" style="font-size:0.75rem;color:rgba(255,255,255,0.3);width:16px;text-align:center;">○</span><span style="font-size:0.8rem;color:rgba(255,255,255,0.6);">${f.label}</span>`;
      container.appendChild(item);
    });
  }

  renderFormPreview() {
    const groups = {
      personal: ['full_name','dob','gender','marital_status','dependents'],
      contact: ['phone','email','address','city','state'],
      employment: ['employment_type','employer_name','monthly_income','work_experience_years'],
      loan: ['loan_amount','loan_purpose','loan_tenure_months'],
      identity: ['pan_number','aadhaar_number','own_property','own_vehicle']
    };
    const containers = {
      personal: document.getElementById('form-personal'),
      contact: document.getElementById('form-contact'),
      employment: document.getElementById('form-employment'),
      loan: document.getElementById('form-loan'),
      identity: document.getElementById('form-identity')
    };
    const groupTitles = {
      personal: '👤 Personal Information',
      contact: '📞 Contact Details',
      employment: '💼 Employment',
      loan: '💰 Loan Details',
      identity: '🪪 Identity'
    };
    
    for (const [group, fieldKeys] of Object.entries(groups)) {
      const container = containers[group];
      if (!container) continue;
      container.innerHTML = `<h4 style="font-size:0.75rem;text-transform:uppercase;letter-spacing:0.1em;color:rgba(99,179,237,0.7);margin-bottom:10px;grid-column:1/-1;">${groupTitles[group]}</h4>`;
      container.style.cssText = 'display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:16px;';
      
      fieldKeys.forEach(key => {
        const fieldDef = this.fields.find(f => f.field_key === key);
        if (!fieldDef) return;
        const div = document.createElement('div');
        div.id = `field-preview-${key}`;
        div.style.cssText = 'background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:8px;padding:8px 10px;transition:all 0.4s ease;';
        div.innerHTML = `<div style="font-size:0.7rem;color:rgba(255,255,255,0.4);margin-bottom:2px;">${fieldDef.label}</div><div class="field-value" style="font-size:0.85rem;color:rgba(255,255,255,0.6);">—</div>`;
        container.appendChild(div);
      });
    }
  }

  highlightCurrentField(fieldKey) {
    document.querySelectorAll('.field-status-item.current').forEach(el => {
      el.classList.remove('current');
    });
    const item = document.getElementById(`check-${fieldKey}`);
    if (item) {
      item.classList.add('current');
      item.style.background = 'rgba(66,153,225,0.1)';
      item.querySelector('.status-icon').textContent = '▶';
    }
  }
}

// Global instance
const assistant = new CredAIAssistant();

// HTML Hook Handlers
function selectLanguage(lang) { assistant.selectLanguage(lang); }
function startAssistant() { assistant.startInterview(); }
function skipField() { assistant.answers[assistant.currentField?.field_key] = null; assistant.askNextQuestion(); }
function repeatQuestion() { if (assistant.currentField) { speakText(assistant.currentField.question_text, assistant.language); } }
function toggleMic() { 
  if (assistant.state === AssistantState.LISTENING) { stopListening(); assistant.setState(AssistantState.IDLE); }
  else { startListening(assistant.language, assistant.handleVoiceTranscript.bind(assistant)); assistant.setState(AssistantState.LISTENING); }
}

function submitTypedAnswer() {
  const input = document.getElementById('typed-answer-input');
  const val = input.value.trim();
  if (!val) return;
  input.value = '';
  document.getElementById('typed-fallback').style.display = 'none';
  assistant.appendUserMessage(val);
  assistant.processAnswer(val);
}

function handlePdfUpload(event) {
    const file = event.target.files[0];
    if(file) {
        assistant.pdfFile = file;
        const status = document.getElementById('pdf-status');
        if(status) {
            status.style.display = 'block';
            status.textContent = `PDF Uploaded: ${file.name}`;
        }
    }
}

function handlePdfDrop(event) {
    event.preventDefault();
    if (event.dataTransfer.items) {
        const file = event.dataTransfer.items[0].getAsFile();
        if(file && file.type === "application/pdf") {
            assistant.pdfFile = file;
            const status = document.getElementById('pdf-status');
            if(status) {
                status.style.display = 'block';
                status.textContent = `PDF Uploaded: ${file.name}`;
            }
        }
    }
}

async function submitApplication() {
  const btn = document.querySelector('#submit-section button');
  btn.textContent = '⏳ Analyzing...';
  btn.disabled = true;
  
  const faceData = window.lastFaceAnalysis || {};
  const payload = {
    session_id: assistant.sessionId || 'sess_' + Date.now(),
    language: assistant.language,
    answers: assistant.answers,
    face_analysis: faceData,
    metadata: { completion_time_seconds: Math.floor((Date.now() - (window.sessionStartTime||Date.now())) / 1000) }
  };
  
  try {
    const result = await fetch('/api/session/complete', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    }).then(r=>r.json());
    
    sessionStorage.setItem('credai_result', JSON.stringify(result));
    window.location.href = 'result.html';
  } catch (err) {
    btn.textContent = '✅ Submit Application';
    btn.disabled = false;
    assistant.appendAssistantMessage("Submission failed. Please try again.");
  }
}
