// ==========================
// 🎙 Alpaca Voice Agent Client
// ==========================

// Media recorder variables
let mediaRecorder;
let audioChunks = [];
let isRecording = false;

// Session ID handling (unique per user/browser session)
let sessionId = new URLSearchParams(window.location.search).get("session_id");
if (!sessionId) {
    sessionId = Date.now().toString();
    window.history.replaceState({}, '', `?session_id=${sessionId}`);
}

// DOM element references
const recordButton = document.getElementById("record-toggle");
const recordingIndicator = document.getElementById("recording-indicator");
const statusDiv = document.getElementById("upload-status");
const playBack = document.getElementById("playback");

// Check for microphone access
if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
    console.log("getUserMedia supported.");
    navigator.mediaDevices.getUserMedia({ audio: true })
        .then((stream) => {
            // Stop immediately, we just needed permission check
            stream.getTracks().forEach(track => track.stop());
        })
        .catch((err) => {
            console.log(`Microphone access error: ${err}`);
            updateStatus("Microphone access denied. Please enable microphone permissions.", true);
        });
} else {
    console.log('getUserMedia not supported on your browser');
    updateStatus("Your browser doesn't support audio recording.", true);
}

// Record button toggle handler
recordButton.addEventListener("click", async () => {
    if (isRecording) {
        stopRecording();
    } else {
        await startRecording();
    }
});

// Start recording audio
async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

        // Initialize MediaRecorder
        mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
        audioChunks = [];
        isRecording = true;

        // Update UI to recording state
        recordButton.textContent = "🛑 Stop Recording";
        recordButton.classList.add("recording");
        recordingIndicator.classList.add("active");

        // Push recorded audio chunks to array
        mediaRecorder.ondataavailable = (e) => {
            audioChunks.push(e.data);
        };

        // When recording stops, process audio
        mediaRecorder.onstop = () => {
            processRecording();
        };

        mediaRecorder.start();
    } catch (err) {
        console.error("Error starting recording:", err);
        updateStatus("Error: Could not access microphone. Please check permissions.", true);
        resetRecordButton();
    }
}

// Stop recording and prepare to process
function stopRecording() {
    if (mediaRecorder && isRecording) {
        mediaRecorder.stop();
        isRecording = false;

        // Stop mic stream
        mediaRecorder.stream.getTracks().forEach(track => track.stop());

        // Update UI to "processing" state
        recordingIndicator.classList.remove("active");
        recordButton.disabled = true;
        recordButton.textContent = "⏳ Processing...";
        recordButton.classList.remove("recording");
        statusDiv.innerHTML = "Processing with LLM...";
        statusDiv.className = "output processing";
    }
}

// Send recorded audio to backend for processing
async function processRecording() {
    try {
        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
        const file = new File([audioBlob], 'recording.webm', { type: 'audio/webm' });
        const formData = new FormData();
        formData.append('file', file);

        // Call backend /agent/chat endpoint
        const response = await fetch(`/agent/chat/${sessionId}`, {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();

        // If backend returned error
        if (data.error) {
            console.warn("Backend error:", data.error);
            if (data.audio_base64) {
                playBase64Audio(data.audio_base64);
                updateStatus(data.transcription || "Voice message received", false, "(Fallback audio played)");
            } else {
                playFallbackAudio();
            }
            return;
        }

        // Show transcription and AI response
        updateStatus(`
            <div class="conversation-message user-message fade-in">
                <div class="message-label">You said:</div>
                <div class="message-text">${data.transcription || "(No transcription)"}</div>
            </div>
            <div class="conversation-message assistant-message fade-in">
                <div class="message-label">Assistant:</div>
                <div class="message-text">${data.text}</div>
            </div>
        `);

        // Decode and play audio response
        try {
            const audioBinary = atob(data.audio_base64);
            const audioBuffer = new Uint8Array(audioBinary.length);
            for (let i = 0; i < audioBinary.length; i++) {
                audioBuffer[i] = audioBinary.charCodeAt(i);
            }
            const audioFileBlob = new Blob([audioBuffer], { type: 'audio/mpeg' });
            const audioURL = URL.createObjectURL(audioFileBlob);

            playBack.src = audioURL;
            playBack.play();
        } catch (err) {
            console.error("Audio decode failed:", err);
            playFallbackAudio();
        }

    } catch (err) {
        console.error("Error talking to backend:", err);
        playFallbackAudio();
    } finally {
        resetRecordButton();
    }
}

// Play backup audio if API call fails
function playFallbackAudio() {
    updateStatus("I'm having trouble connecting right now, but I'm still here.", false, "Connection issue");
    const fallbackAudio = new Audio("/static/fallback.mp3");
    fallbackAudio.play().catch(err => console.warn("Fallback audio failed:", err));
}

// Decode base64-encoded audio and play it
function playBase64Audio(base64Data) {
    try {
        const audioBinary = atob(base64Data);
        const audioBuffer = new Uint8Array(audioBinary.length);
        for (let i = 0; i < audioBinary.length; i++) {
            audioBuffer[i] = audioBinary.charCodeAt(i);
        }
        const audioFileBlob = new Blob([audioBuffer], { type: 'audio/mpeg' });
        const audioURL = URL.createObjectURL(audioFileBlob);

        playBack.src = audioURL;
        playBack.play().catch(err => {
            console.error("Audio playback failed:", err);
        });
    } catch (err) {
        console.error("Base64 decode failed:", err);
        playFallbackAudio();
    }
}

// Update status box with messages
function updateStatus(content, isError = false, note = null) {
    statusDiv.className = "output";
    if (isError) {
        statusDiv.innerHTML = `<div class="error-message">${content}</div>`;
    } else {
        statusDiv.innerHTML = content;
    }
    if (note) {
        statusDiv.innerHTML += `<div style="color: red; font-size: 0.85rem; margin-top: 0.5rem; font-style: italic;">${note}</div>`;
    }
}

// Reset record button to default state
function resetRecordButton() {
    recordButton.disabled = false;
    recordButton.classList.remove("recording");
    recordButton.textContent = "🎤 Start Recording";
}

// Auto-restart recording after audio playback ends
playBack.addEventListener('ended', () => {
    setTimeout(() => {
        if (!isRecording) {
            startRecording();
        }
    }, 500);
});
