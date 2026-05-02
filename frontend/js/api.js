const BASE_URL = window.location.origin;

async function fetchAPI(endpoint, options = {}, timeoutMs = 30000) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
    try {
        const response = await fetch(`${BASE_URL}${endpoint}`, {
            ...options,
            signal: controller.signal
        });
        clearTimeout(timeoutId);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        clearTimeout(timeoutId);
        if (error.name === 'AbortError') {
            throw new Error('Request timed out. Please try again.');
        }
        console.error("API Error:", error);
        throw error;
    }
}

async function getIPCity() {
    try {
        const res = await fetch("https://ip-api.com/json?fields=city,status");
        const data = await res.json();
        return data.status === "success" ? data.city : "";
    } catch { return ""; }
}

async function analyzeface(imageBlob) {
    const formData = new FormData();
    formData.append("image", imageBlob, "snapshot.jpg");
    return await fetchAPI("/api/face-analyze", {
        method: "POST",
        body: formData
    }, 60000);
}

async function verifyFaces(img1Blob, img2Blob) {
    const formData = new FormData();
    formData.append("img1", img1Blob, "live.jpg");
    formData.append("img2", img2Blob, "id.jpg");
    return await fetchAPI("/api/face-verify", {
        method: "POST",
        body: formData
    }, 60000);
}

async function predictRisk(formData) {
    return await fetchAPI("/api/risk", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData)
    });
}

async function detectFraud(sessionData) {
    return await fetchAPI("/api/fraud", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(sessionData)
    });
}

async function startSession() {
    return await fetchAPI("/api/session/start", { method: "POST" });
}

async function submitApplication(allData, sessionId) {
    const payload = {
        session_id: sessionId,
        applicant_data: allData,
        pan_number: allData.pan_number || ""
    };
    
    const result = await fetchAPI("/api/session/complete", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    });
    
    if (result.success) {
        sessionStorage.setItem("applicationResult", JSON.stringify(result));
        sessionStorage.setItem("applicantData", JSON.stringify(allData));
        window.location.href = "result.html";
    }
    
    return result;
}

// Health check polling
function initHealthCheck() {
    const dot = document.getElementById("api-status-dot");
    const text = document.getElementById("api-status-text");
    
    async function check() {
        try {
            const res = await fetch(`${BASE_URL}/api/health`);
            if (res.ok) {
                if (dot) {
                    dot.className = "status-dot online";
                    text.innerText = "Backend Connected";
                }
            } else {
                throw new Error("Not ok");
            }
        } catch (e) {
            if (dot) {
                dot.className = "status-dot offline";
                text.innerText = "Backend Offline";
            }
        }
    }
    
    check();
    setInterval(check, 5000);
}

document.addEventListener("DOMContentLoaded", () => {
    // Only inject health status if container exists
    if (!document.getElementById("api-status-container")) {
        const div = document.createElement('div');
        div.className = "api-status";
        div.id = "api-status-container";
        div.innerHTML = `<div id="api-status-dot" class="status-dot offline"></div><span id="api-status-text">Checking...</span>`;
        document.body.appendChild(div);
    }
    initHealthCheck();
});
