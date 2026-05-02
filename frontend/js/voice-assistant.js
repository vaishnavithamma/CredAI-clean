// Voice Assistant Logic for CredAI

const VA_STATE = {
    estimatedAge: 0,
    langCode: 'en-IN',
    langKey: 'en',
    mode: '', // 'document' or 'voice'
    qIndex: 0,
    collectedData: {},
    isListening: false,
    retryTimer: null,
    currentUtterance: null
};

const VA_LANG_MAP = {
    'en': 'en-IN',
    'kn': 'kn-IN',
    'hi': 'hi-IN'
};

const VA_LANG_LABELS = {
    'en': 'English',
    'kn': 'ಕನ್ನಡ',
    'hi': 'हिन्दी'
};

const VA_QUESTIONS = [
    { key: "fullname", en: "What is your full name?", kn: "ನಿಮ್ಮ ಪೂರ್ಣ ಹೆಸರು ಏನು?", hi: "आपका पूरा नाम क्या है?" },
    { key: "dob", en: "What is your date of birth?", kn: "ನಿಮ್ಮ ಹುಟ್ಟಿದ ದಿನಾಂಕ ಯಾವುದು?", hi: "आपकी जन्म तिथि क्या है?" },
    { key: "confirm_age", en: "Our system detected your age as {age}. Can you confirm this?", kn: "ನಮ್ಮ ವ್ಯವಸ್ಥೆ ನಿಮ್ಮ ವಯಸ್ಸನ್ನು {age} ಎಂದು ಪತ್ತೆ ಮಾಡಿದೆ. ದೃಢೀಕರಿಸಬಹುದೇ?", hi: "हमारे सिस्टम ने आपकी उम्र {age} वर्ष पाई है। क्या आप इसकी पुष्टि करते हैं?" },
    { key: "phone", en: "What is your phone number?", kn: "ನಿಮ್ಮ ಫೋನ್ ನಂಬರ್ ಏನು?", hi: "आपका फोन नंबर क्या है?" },
    { key: "city", en: "What is your current city?", kn: "ನಿಮ್ಮ ಪ್ರಸ್ತುತ ವಿಳಾಸ ಏನು?", hi: "आपका वर्तमान शहर क्या है?" },
    { key: "employment_type", en: "What is your employment status? Are you salaried, self-employed, or a pensioner?", kn: "ನಿಮ್ಮ ಉದ್ಯೋಗ ಸ್ಥಿತಿ ಏನು? ನೀವು ವೇತನದಾರ, ಸ್ವಯಂ ಉದ್ಯೋಗ, ಅಥವಾ ಪಿಂಚಣಿದಾರರೇ?", hi: "आपकी रोज़गार स्थिति क्या है? आप वेतनभोगी हैं, स्वरोज़गार हैं, या पेंशनभोगी?" },
    { key: "income", en: "What is your monthly income in rupees?", kn: "ನಿಮ್ಮ ಮಾಸಿಕ ಆದಾಯ ಎಷ್ಟು ರೂಪಾಯಿ?", hi: "आपकी मासिक आय कितनी है रुपयों में?" },
    { key: "employment_years", en: "How many years have you been employed?", kn: "ನೀವು ಎಷ್ಟು ವರ್ಷಗಳಿಂದ ಉದ್ಯೋಗದಲ್ಲಿದ್ದೀರಿ?", hi: "आप कितने सालों से नौकरी में हैं?" },
    { key: "loan_amount", en: "How much loan amount are you requesting in rupees?", kn: "ನೀವು ಎಷ್ಟು ರೂಪಾಯಿ ಸಾಲ ಬೇಡುತ್ತಿದ್ದೀರಿ?", hi: "आप कितने रुपये का लोन मांग रहे हैं?" },
    { key: "loan_purpose", en: "What is the purpose of this loan?", kn: "ಈ ಸಾಲದ ಉದ್ದೇಶ ಏನು?", hi: "इस लोन का उद्देश्य क्या है?" },
    { key: "existing_loans", en: "Do you have any existing loans? Say yes or no.", kn: "ನಿಮಗೆ ಈಗಾಗಲೇ ಯಾವುದಾದರೂ ಸಾಲ ಇದೆಯೇ? ಹೌದು ಅಥವಾ ಇಲ್ಲ ಎನ್ನಿ.", hi: "क्या आपके पास पहले से कोई लोन है? हाँ या नहीं कहें।" },
    { key: "credit_history_aware", en: "Are you aware of your credit history?", kn: "ನಿಮ್ಮ ಕ್ರೆಡಿಟ್ ಇತಿಹಾಸದ ಬಗ್ಗೆ ನಿಮಗೆ ತಿಳಿದಿದೆಯೇ?", hi: "क्या आप अपने क्रेडिट इतिहास के बारे में जानते हैं?" },
    { key: "family_status", en: "What is your marital status? Married, single, or other?", kn: "ನಿಮ್ಮ ವೈವಾಹಿಕ ಸ್ಥಿತಿ ಏನು? ವಿವಾಹಿತ, ಅವಿವಾಹಿತ ಅಥವಾ ಇತರ?", hi: "आपकी वैवाहिक स्थिति क्या है? विवाहित, अविवाहित, या अन्य?" },
    { key: "own_car", en: "Do you own a car? Say yes or no.", kn: "ನಿಮ್ಮ ಬಳಿ ಕಾರು ಇದೆಯೇ?", hi: "क्या आपके पास कार है? हाँ या नहीं।" },
    { key: "own_realty", en: "Do you own any property or real estate? Say yes or no.", kn: "ನಿಮ್ಮ ಬಳಿ ಯಾವುದಾದರೂ ಆಸ್ತಿ ಅಥವಾ ರಿಯಲ್ ಎಸ್ಟೇಟ್ ಇದೆಯೇ?", hi: "क्या आपके पास कोई संपत्ति है? हाँ या नहीं।" },
    { key: "children", en: "How many children do you have?", kn: "ನಿಮಗೆ ಎಷ್ಟು ಮಕ್ಕಳಿದ್ದಾರೆ?", hi: "आपके कितने बच्चे हैं?" }
];

// Entry Point
window.launchVoiceAssistant = function(estimatedAge) {
    VA_STATE.estimatedAge = estimatedAge;
    document.getElementById('va-overlay').style.display = 'flex';
    vaShowView('lang');
    
    // Initial welcome
    vaSpeak("Welcome to CredAI. Please choose your preferred language.", "en-IN", () => {
        vaStartListeningForLanguage();
    });
};

function vaShowView(viewName) {
    ['lang', 'mode', 'doc', 'qa'].forEach(v => {
        document.getElementById(`va-view-${v}`).style.display = (v === viewName) ? 'block' : 'none';
    });
}

function vaSkipFlow() {
    vaStopListening();
    if(window.speechSynthesis.speaking) window.speechSynthesis.cancel();
    document.getElementById('va-overlay').style.display = 'none';
}

// ================= STT & TTS =================

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognition = null;
if (SpeechRecognition) {
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
} else {
    console.warn("Speech Recognition API not supported in this browser.");
}

function vaSpeak(text, lang, onEndCallback) {
    if(window.speechSynthesis.speaking) {
        window.speechSynthesis.cancel();
    }
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = lang;
    utterance.rate = 0.9;
    utterance.pitch = 1.0;
    
    document.getElementById('va-ai-response').innerText = text;
    
    utterance.onend = () => {
        if (onEndCallback) onEndCallback();
    };
    
    VA_STATE.currentUtterance = utterance;
    window.speechSynthesis.speak(utterance);
}

function vaStartListening(onResultCallback, onEndCallback, langCode = 'en-IN') {
    if (!recognition) return;
    
    // reset visuals
    const micIcon = document.getElementById('va-avatar');
    micIcon.style.boxShadow = '0 0 20px rgba(0, 212, 255, 0.8)';
    micIcon.style.transform = 'scale(1.1)';
    document.getElementById('va-transcript').innerText = 'Listening...';
    
    recognition.lang = langCode;
    recognition.onresult = (e) => {
        let interim = '';
        let final = '';
        for (let i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                final += e.results[i][0].transcript;
            } else {
                interim += e.results[i][0].transcript;
            }
        }
        document.getElementById('va-transcript').innerText = final || interim;
        
        if (final && onResultCallback) {
            onResultCallback(final.trim().toLowerCase());
        }
    };
    
    recognition.onerror = (e) => {
        console.error("Speech Recognition Error:", e.error);
        if (e.error === 'no-speech') {
            vaHandleSilence();
        }
    };
    
    recognition.onend = () => {
        micIcon.style.boxShadow = 'none';
        micIcon.style.transform = 'scale(1)';
        if (onEndCallback) onEndCallback();
    };
    
    clearTimeout(VA_STATE.retryTimer);
    VA_STATE.retryTimer = setTimeout(() => {
        recognition.stop();
        vaHandleSilence();
    }, 10000); // 10 second timeout for silence
    
    try {
        recognition.start();
        VA_STATE.isListening = true;
    } catch(e) { console.log(e); }
}

function vaStopListening() {
    if (recognition && VA_STATE.isListening) {
        recognition.stop();
        VA_STATE.isListening = false;
        clearTimeout(VA_STATE.retryTimer);
    }
}

function vaHandleSilence() {
    vaStopListening();
    const prompt = {
        'en': "I didn't catch that. Could you please repeat?",
        'kn': "ನನಗೆ ಕೇಳಿಸಲಿಲ್ಲ. ದಯವಿಟ್ಟು ಮತ್ತೊಮ್ಮೆ ಹೇಳುವಿರಾ?",
        'hi': "मुझे समझ नहीं आया। क्या आप दोहरा सकते हैं?"
    }[VA_STATE.langKey];
    
    vaSpeak(prompt, VA_STATE.langCode, () => {
        // restart listening for current context
        if (document.getElementById('va-view-lang').style.display === 'block') {
            vaStartListeningForLanguage();
        } else if (document.getElementById('va-view-mode').style.display === 'block') {
            vaStartListeningForMode();
        } else if (document.getElementById('va-view-qa').style.display === 'block') {
            vaAskCurrentQuestion();
        }
    });
}

// ================= STEP A: LANGUAGE =================

function vaStartListeningForLanguage() {
    vaStartListening((transcript) => {
        vaStopListening();
        if (transcript.includes('english')) vaSetLanguage('en');
        else if (transcript.includes('kannada') || transcript.includes('ಕನ್ನಡ')) vaSetLanguage('kn');
        else if (transcript.includes('hindi') || transcript.includes('हिन्दी')) vaSetLanguage('hi');
        else vaHandleSilence();
    }, null, 'en-IN');
}

window.vaSetLanguage = function(langKey) {
    vaStopListening();
    if(window.speechSynthesis.speaking) window.speechSynthesis.cancel();
    
    VA_STATE.langKey = langKey;
    VA_STATE.langCode = VA_LANG_MAP[langKey];
    
    document.getElementById('va-lang-badge').innerText = VA_LANG_LABELS[langKey];
    document.getElementById('va-lang-badge').style.display = 'inline-block';
    
    vaShowModeSelection();
};

// ================= STEP B: MODE =================

function vaShowModeSelection() {
    vaShowView('mode');
    
    const prompts = {
        'en': "How would you like to complete your loan application? Option 1: Upload your existing loan document. Option 2: Answer questions by speaking.",
        'kn': "ನೀವು ನಿಮ್ಮ ಸಾಲದ ಅರ್ಜಿಯನ್ನು ಹೇಗೆ ಭರ್ತಿ ಮಾಡಲು ಬಯಸುತ್ತೀರಿ? ಆಯ್ಕೆ 1: ದಾಖಲೆ ಅಪ್ಲೋಡ್ ಮಾಡಿ. ಆಯ್ಕೆ 2: ಧ್ವನಿ ಮೂಲಕ ಉತ್ತರಿಸಿ.",
        'hi': "आप अपना लोन आवेदन कैसे पूरा करना चाहेंगे? विकल्प 1: दस्तावेज़ अपलोड करें। विकल्प 2: बोलकर उत्तर दें।"
    };
    
    document.getElementById('va-mode-title').innerText = {
        'en': "How would you like to complete?",
        'kn': "ನೀವು ಹೇಗೆ ಮುಂದುವರಿಯಲು ಬಯಸುತ್ತೀರಿ?",
        'hi': "आप कैसे आगे बढ़ना चाहेंगे?"
    }[VA_STATE.langKey];
    
    vaSpeak(prompts[VA_STATE.langKey], VA_STATE.langCode, () => {
        vaStartListeningForMode();
    });
}

function vaStartListeningForMode() {
    vaStartListening((transcript) => {
        vaStopListening();
        const str = transcript.toLowerCase();
        if (str.includes('upload') || str.includes('document') || str.includes('1') || str.includes('one') || str.includes('ದಾಖಲೆ') || str.includes('दस्तावेज़')) {
            vaSetMode('document');
        } else if (str.includes('voice') || str.includes('speak') || str.includes('2') || str.includes('two') || str.includes('ಧ್ವನಿ') || str.includes('बोलकर')) {
            vaSetMode('voice');
        } else {
            vaHandleSilence();
        }
    }, null, VA_STATE.langCode);
}

window.vaSetMode = function(mode) {
    vaStopListening();
    if(window.speechSynthesis.speaking) window.speechSynthesis.cancel();
    
    VA_STATE.mode = mode;
    if (mode === 'document') {
        vaShowView('doc');
        document.getElementById('va-doc-title').innerText = {
            'en': "Upload Document", 'kn': "ದಾಖಲೆ ಅಪ್ಲೋಡ್", 'hi': "दस्तावेज़ अपलोड"
        }[VA_STATE.langKey];
        document.getElementById('va-doc-btn').innerText = {
            'en': "Process Document", 'kn': "ಪರಿಶೀಲಿಸಿ", 'hi': "प्रोसेस करें"
        }[VA_STATE.langKey];
    } else {
        vaStartQA();
    }
};

// ================= STEP C: DOCUMENT OCR =================

window.vaProcessDocument = async function() {
    const fileInput = document.getElementById('va-doc-input');
    if (!fileInput.files.length) return;
    
    const file = fileInput.files[0];
    document.getElementById('va-doc-status').innerText = "Processing document, please wait...";
    
    try {
        let imgUrl = URL.createObjectURL(file);
        
        // Handle PDF via PDF.js
        if (file.type === "application/pdf") {
            document.getElementById('va-doc-status').innerText = "Converting PDF to image...";
            const pdfjsLib = window['pdfjs-dist/build/pdf'];
            pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
            const arrayBuffer = await file.arrayBuffer();
            const pdf = await pdfjsLib.getDocument(arrayBuffer).promise;
            const page = await pdf.getPage(1);
            const viewport = page.getViewport({scale: 1.5});
            const canvas = document.createElement('canvas');
            canvas.width = viewport.width;
            canvas.height = viewport.height;
            await page.render({canvasContext: canvas.getContext('2d'), viewport: viewport}).promise;
            imgUrl = canvas.toDataURL('image/jpeg');
        }

        document.getElementById('va-doc-status').innerText = "Extracting text with AI...";
        const worker = await Tesseract.createWorker('eng');
        const ret = await worker.recognize(imgUrl);
        const text = ret.data.text;
        await worker.terminate();
        
        console.log("OCR Extracted Text:\n", text);
        
        // Simple Regex Extraction
        let nameMatch = text.match(/(?:Name|NAME)[\s:]+([A-Za-z ]+)/);
        let dobMatch = text.match(/(?:DOB|Date of Birth|Birth)[\s:]+([\d]{2}[\/\-][\d]{2}[\/\-][\d]{4})/);
        let incomeMatch = text.match(/(?:Income|Salary|Pay)[\s:]+(?:Rs\.?|INR|₹)?\s*([\d,]+)/i);
        let amountMatch = text.match(/(?:Loan Amount|Amount Required)[\s:]+(?:Rs\.?|INR|₹)?\s*([\d,]+)/i);
        
        if (nameMatch) VA_STATE.collectedData['fullname'] = nameMatch[1].trim();
        if (dobMatch) VA_STATE.collectedData['dob'] = dobMatch[1].trim();
        if (incomeMatch) VA_STATE.collectedData['income'] = incomeMatch[1].replace(/,/g, '').trim();
        if (amountMatch) VA_STATE.collectedData['loan_amount'] = amountMatch[1].replace(/,/g, '').trim();
        
        document.getElementById('va-doc-status').innerText = "Extraction complete!";
        
        const summaryEn = `I found your name as ${VA_STATE.collectedData['fullname'] || 'unknown'}, income ${VA_STATE.collectedData['income'] || 'unknown'}. Is this correct? Say yes or no.`;
        const summaryKn = `ನಾನು ನಿಮ್ಮ ಹೆಸರು ${VA_STATE.collectedData['fullname'] || 'ತಿಳಿದಿಲ್ಲ'}, ಆದಾಯ ${VA_STATE.collectedData['income'] || 'ತಿಳಿದಿಲ್ಲ'} ಕಂಡುಕೊಂಡಿದ್ದೇನೆ. ಇದು ಸರಿಯಾಗಿದೆಯೇ?`;
        const summaryHi = `मुझे आपका नाम ${VA_STATE.collectedData['fullname'] || 'अज्ञात'}, आय ${VA_STATE.collectedData['income'] || 'अज्ञात'} मिली। क्या यह सही है?`;
        
        const summaryMsg = { 'en': summaryEn, 'kn': summaryKn, 'hi': summaryHi }[VA_STATE.langKey];
        
        vaSpeak(summaryMsg, VA_STATE.langCode, () => {
            vaStartListening((transcript) => {
                vaStopListening();
                if (transcript.includes('no') || transcript.includes('ಇಲ್ಲ') || transcript.includes('नहीं')) {
                    // reset collected data from doc and go to voice flow
                    VA_STATE.collectedData = {};
                }
                vaStartQA();
            }, null, VA_STATE.langCode);
        });

    } catch (e) {
        console.error(e);
        document.getElementById('va-doc-status').innerText = "Error extracting text. Switching to voice.";
        setTimeout(() => vaStartQA(), 2000);
    }
}

// ================= STEP D: VOICE Q&A =================

function vaStartQA() {
    vaShowView('qa');
    VA_STATE.qIndex = 0;
    vaAskCurrentQuestion();
}

window.vaSkipQuestion = function() {
    vaStopListening();
    if(window.speechSynthesis.speaking) window.speechSynthesis.cancel();
    VA_STATE.qIndex++;
    vaAskCurrentQuestion();
};

function vaAskCurrentQuestion() {
    // skip questions already populated by OCR
    while (VA_STATE.qIndex < VA_QUESTIONS.length && VA_STATE.collectedData[VA_QUESTIONS[VA_STATE.qIndex].key]) {
        VA_STATE.qIndex++;
    }

    if (VA_STATE.qIndex >= VA_QUESTIONS.length) {
        vaFinishFlow();
        return;
    }

    const progress = (VA_STATE.qIndex / VA_QUESTIONS.length) * 100;
    document.getElementById('va-progress').style.width = `${progress}%`;

    const qObj = VA_QUESTIONS[VA_STATE.qIndex];
    let qText = qObj[VA_STATE.langKey];
    
    // Replace dynamic variables
    if (qObj.key === "confirm_age") {
        qText = qText.replace("{age}", VA_STATE.estimatedAge);
    }
    
    document.getElementById('va-question-text').innerText = qText;
    
    vaSpeak(qText, VA_STATE.langCode, () => {
        vaStartListening((transcript) => {
            vaStopListening();
            vaProcessAnswer(transcript);
        }, null, VA_STATE.langCode);
    });
}

function vaProcessAnswer(transcript) {
    const qObj = VA_QUESTIONS[VA_STATE.qIndex];
    const key = qObj.key;
    
    if (transcript.includes('skip') || transcript.includes('स्किप') || transcript.includes('ಸ್ಕಿಪ್')) {
        VA_STATE.qIndex++;
        vaAskCurrentQuestion();
        return;
    }
    
    if (transcript.includes('repeat') || transcript.includes('ಮತ್ತೊಮ್ಮೆ') || transcript.includes('दोहरा')) {
        vaAskCurrentQuestion();
        return;
    }

    // Age validation logic
    if (key === "confirm_age") {
        // Simple heuristic: extract number
        const numMatch = transcript.match(/\d+/);
        if (transcript.includes('no') || transcript.includes('ಇಲ್ಲ') || transcript.includes('नहीं') || numMatch) {
            let spokenAge = numMatch ? parseInt(numMatch[0]) : VA_STATE.estimatedAge;
            if (Math.abs(spokenAge - VA_STATE.estimatedAge) > 8 && !transcript.includes('yes')) {
                const warnMsg = {
                    'en': `There seems to be a mismatch. Our system detected ${VA_STATE.estimatedAge} but you indicated otherwise. Proceeding anyway.`,
                    'kn': `ವಯಸ್ಸಿನಲ್ಲಿ ವ್ಯತ್ಯಾಸವಿದೆ. ಆದರೂ ನಾವು ಮುಂದುವರಿಯುತ್ತಿದ್ದೇವೆ.`,
                    'hi': `उम्र में अंतर प्रतीत होता है। हम फिर भी आगे बढ़ रहे हैं।`
                }[VA_STATE.langKey];
                vaSpeak(warnMsg, VA_STATE.langCode, () => {
                    VA_STATE.collectedData['age'] = spokenAge;
                    VA_STATE.qIndex++;
                    vaAskCurrentQuestion();
                });
                return;
            }
        }
    }

    // Save answer
    VA_STATE.collectedData[key] = transcript;
    
    VA_STATE.qIndex++;
    setTimeout(() => vaAskCurrentQuestion(), 500);
}

// ================= COMPLETION =================

function vaFinishFlow() {
    const finishMsg = {
        'en': "Thank you. I have collected all the details. Proceeding to final review.",
        'kn': "ಧನ್ಯವಾದಗಳು. ನಾನು ಎಲ್ಲಾ ವಿವರಗಳನ್ನು ಸಂಗ್ರಹಿಸಿದ್ದೇನೆ.",
        'hi': "धन्यवाद। मैंने सभी विवरण एकत्र कर लिए हैं।"
    }[VA_STATE.langKey];
    
    document.getElementById('va-question-text').innerText = "Processing your application...";
    document.getElementById('va-transcript').innerText = "";
    
    vaSpeak(finishMsg, VA_STATE.langCode, () => {
        // Auto-fill forms
        document.getElementById('va-overlay').style.display = 'none';
        
        // Merge into applicantData
        window.applicantData.fullname = VA_STATE.collectedData['fullname'] || '';
        window.applicantData.city = VA_STATE.collectedData['city'] || '';
        window.applicantData.dob = VA_STATE.collectedData['dob'] || '';
        window.applicantData.income = (VA_STATE.collectedData['income'] || '').replace(/\D/g, '');
        window.applicantData.loan_amount = (VA_STATE.collectedData['loan_amount'] || '').replace(/\D/g, '');
        window.applicantData.employment_years = (VA_STATE.collectedData['employment_years'] || '').replace(/\D/g, '');
        window.applicantData.children = (VA_STATE.collectedData['children'] || '').replace(/\D/g, '');
        window.applicantData.source = VA_STATE.mode;
        
        // Fill UI inputs
        if(document.getElementById('fullname')) document.getElementById('fullname').value = window.applicantData.fullname;
        if(document.getElementById('city')) document.getElementById('city').value = window.applicantData.city;
        if(document.getElementById('income')) document.getElementById('income').value = window.applicantData.income;
        if(document.getElementById('loan_amount')) document.getElementById('loan_amount').value = window.applicantData.loan_amount;
        if(document.getElementById('employment_years')) document.getElementById('employment_years').value = window.applicantData.employment_years;
        if(document.getElementById('children')) document.getElementById('children').value = window.applicantData.children;
        
        // Enum mapping (naive matching)
        if(VA_STATE.collectedData['family_status']) {
            if(VA_STATE.collectedData['family_status'].includes('single')) document.getElementById('family_status').value = 'Single / not married';
        }
        if(VA_STATE.collectedData['own_car']) {
            if(VA_STATE.collectedData['own_car'].includes('yes')) document.getElementById('own_car').value = 'Y';
        }
        if(VA_STATE.collectedData['own_realty']) {
            if(VA_STATE.collectedData['own_realty'].includes('yes')) document.getElementById('own_realty').value = 'Y';
        }
        if(VA_STATE.collectedData['income_type']) {
            if(VA_STATE.collectedData['income_type'].includes('business')) document.getElementById('employment_type').value = 'Commercial associate';
            else if(VA_STATE.collectedData['income_type'].includes('pension')) document.getElementById('employment_type').value = 'Pensioner';
        }
        
        if (window.showToast) {
            window.showToast("✅ Details collected via voice. Please review and submit.", "success");
        }
        
        // Jump to step 4
        if (window.currentStep !== undefined) {
            window.currentStep = 4;
            if (typeof window.updateUI === 'function') window.updateUI();
            else {
                // Inline update UI if the function isn't exposed globally
                document.querySelectorAll('.step-panel').forEach((panel, index) => {
                    panel.classList.toggle('active', index + 1 === 4);
                });
                document.querySelectorAll('.stepper-item').forEach((item, index) => {
                    if(index < 3) item.classList.add('completed');
                    item.classList.toggle('active', index + 1 === 4);
                });
            }
        }
    });
}
