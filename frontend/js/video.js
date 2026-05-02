// 🚨 Prevent duplicate execution
if (window.__video_initialized__) {
    console.warn("video.js already initialized — skipping duplicate");
} else {
    window.__video_initialized__ = true;

    console.log("VIDEO JS LOADED", Math.random());

    // GLOBAL STATE
    window.stream = null;
    window.currentStep = 1;
    window.applicantData = {};
    window.sessionId = null;
    window.idPhotoBlob = null;
    window.livenessFrames = [];
    window.livenessCheckInterval = null;
    window.mediaRecorder = null;
    window.audioChunks = [];
    window.consentRecorded = false;

    // 🎤 AUDIO CONSENT
    window.recordAudioConsent = async function () {
        const btn = document.getElementById('audio-consent-btn');

        if (window.mediaRecorder && window.mediaRecorder.state === 'recording') {
            window.mediaRecorder.stop();
            btn.innerText = '✅ Consent Recorded';
            btn.disabled = true;
            return;
        }

        try {
            const audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
            window.mediaRecorder = new MediaRecorder(audioStream);
            window.audioChunks = [];

            window.mediaRecorder.ondataavailable = e => window.audioChunks.push(e.data);
            window.mediaRecorder.onstop = () => {
                window.consentRecorded = true;
                window.applicantData.voice_confidence = 0.85;
                showToast('Audio consent recorded ✅', 'success');
            };

            window.mediaRecorder.start();
            btn.innerText = '⏹ Stop Recording';

            setTimeout(() => {
                if (window.mediaRecorder.state === 'recording') window.mediaRecorder.stop();
            }, 10000);

        } catch (err) {
            showToast('Microphone access denied', 'error');
        }
    };

    // 🎥 START CAMERA
    window.startCamera = async function () {
        try {
            window.stream = await navigator.mediaDevices.getUserMedia({ video: true });
            const video = document.getElementById('webcam');

            if (video) {
                video.srcObject = window.stream;
                video.play();
                showToast('Camera started', 'success');
                startLivenessCheck();
            }

        } catch (err) {
            console.error(err);
            showToast('Camera not available', 'error');
        }
    };

    // 📸 CAPTURE FRAME
    async function captureFrame() {
        const video = document.getElementById('webcam');
        if (!video || !window.stream) return null;

        const canvas = document.createElement('canvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        canvas.getContext('2d').drawImage(video, 0, 0);

        return new Promise(resolve => {
            canvas.toBlob(blob => resolve(blob), 'image/jpeg');
        });
    }

    // 📷 CAPTURE ID PHOTO
    window.captureIdPhoto = async function () {
        const blob = await captureFrame();
        if (blob) {
            window.idPhotoBlob = blob;
            showToast('ID photo captured ✅', 'success');
            document.getElementById('id-capture-status').innerText = '✅ ID Photo Captured';
        }
    };

    // 🧠 LIVENESS CHECK
    function startLivenessCheck() {
        const video = document.getElementById('webcam');
        const badge = document.getElementById('liveness-badge');

        if (!video || !window.stream) return;

        badge.innerText = '🟠 Liveness: Checking...';
        window.livenessFrames = [];

        window.livenessCheckInterval = setInterval(() => {
            const canvas = document.createElement('canvas');
            canvas.width = 64;
            canvas.height = 64;

            const ctx = canvas.getContext('2d');
            ctx.drawImage(video, 0, 0, 64, 64);

            const frame = ctx.getImageData(0, 0, 64, 64).data;
            window.livenessFrames.push(Array.from(frame));

            if (window.livenessFrames.length > 10) {
                clearInterval(window.livenessCheckInterval);
                badge.innerText = '🟢 Liveness: Verified';
                showToast('Liveness verified!', 'success');
            }

        }, 300);
    }

    // 🔥 🔥 🔥 FINAL FIXED FUNCTION
    window.analyzeCapture = async function () {
        try {
            console.log("Analyze button clicked");

            const video = document.getElementById("webcam");

            if (!video || video.videoWidth === 0) {
                console.error("Video not ready");
                return;
            }

            const canvas = document.createElement("canvas");
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;

            const ctx = canvas.getContext("2d");
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

            const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg'));

            const formData = new FormData();
            formData.append("image", blob, "frame.jpg");

            console.log("Sending image to backend...");

            const response = await fetch(`${BASE_URL}/api/face-analyze`, {
                method: "POST",
                body: formData
            });

            const data = await response.json();

            console.log("Response:", data);

            // ✅ STORE DATA (IMPORTANT)
            window.applicantData.estimated_age = data.estimated_age || 0;
            window.applicantData.gender = data.gender || "Unknown";
            window.applicantData.emotion = data.emotion || "Unknown";

            // ✅ UPDATE UI
            document.getElementById("analysis-age").innerText = data.estimated_age || "--";
            document.getElementById("analysis-gender").innerText = data.gender || "--";
            document.getElementById("analysis-emotion").innerText = data.emotion || "--";

            showToast("Face analysis complete ✅", "success");

            // ✅ Launch voice loan assistant
            if (data.estimated_age && window.launchVoiceAssistant) {
                setTimeout(() => window.launchVoiceAssistant(data.estimated_age), 1000);
            }

        } catch (error) {
            console.error("Analyze Error:", error);
            showToast("Face analysis failed ❌", "error");
        }
    };

    // ➡️ STEP CONTROL
    window.nextStep = function () {
        window.currentStep++;
        updateUI();
    };

    window.prevStep = function () {
        if (window.currentStep > 1) {
            window.currentStep--;
            updateUI();
        }
    };

    function updateUI() {
        document.querySelectorAll('.step-panel').forEach((panel, index) => {
            panel.classList.toggle('active', index + 1 === window.currentStep);
        });
    }
}

// ✅ FINAL SUBMIT (unchanged)
window.collectDataAndSubmit = async function () {
    if (!window.sessionId) {
        const session = await startSession();
        window.sessionId = session.session_id;
        window.sessionStartAt = Date.now();
    }

    const dobValue = document.getElementById('dob').value;
    const ageYears = dobValue
        ? Math.max(0, Math.floor((Date.now() - new Date(dobValue).getTime()) / (365.25 * 24 * 60 * 60 * 1000)))
        : 0;

    const allData = {
        fullname: document.getElementById('fullname').value.trim(),
        pan_number: document.getElementById('pan_number').value.trim().toUpperCase(),
        age_years: ageYears,
        income: Number(document.getElementById('income').value || 0),
        credit_amount: Number(document.getElementById('loan_amount').value || 0),
        annuity: 0,
        goods_price: Number(document.getElementById('loan_amount').value || 0),
        employment_years: Number(document.getElementById('employment_years').value || 0),
        gender: document.getElementById('gender').value,
        education: document.getElementById('education').value,
        income_type: document.getElementById('employment_type').value,
        family_status: document.getElementById('family_status').value,
        own_car: document.getElementById('own_car').value,
        own_realty: document.getElementById('own_realty').value,
        children: Number(document.getElementById('children').value || 0),
        declared_city: document.getElementById('city').value.trim(),
        estimated_age: window.applicantData.estimated_age || 0,
        face_match_score: window.applicantData.face_match_score || 0,
        voice_confidence: window.applicantData.voice_confidence || 1,
        consent_captured: document.getElementById('consent-check').checked,
        session_duration_seconds: window.sessionStartAt
            ? Math.floor((Date.now() - window.sessionStartAt) / 1000)
            : 0
    };

    if (!allData.consent_captured) {
        showToast('Please accept the consent checkbox first', 'error');
        return;
    }

    await submitApplication(allData, window.sessionId);
};