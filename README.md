# 🎙️ Alpaca Voice Agent

## 📖 Overview
The **Alpaca Voice Agent** is an AI-powered conversational assistant that listens, thinks, and talks back — all in real time.  
It uses **AssemblyAI** for speech-to-text (STT), **OpenAI** for generating intelligent responses, and **TTS APIs** for natural audio playback.  
With a sleek UI and robust error handling, it delivers a smooth, interactive voice experience right in your browser.

---

## ✨ Features
- 🎤 **Speech-to-Text (STT)** — Converts spoken words into text with AssemblyAI.
- 🧠 **Conversational AI** — Uses LLMs to generate natural, context-aware responses.
- 🔊 **Text-to-Speech (TTS)** — Plays responses in realistic, human-like voices.
- ⚠️ **Error Handling** — Returns fallback audio like *"I'm having trouble connecting right now"* if APIs fail.
- 💻 **Clean UI** — Simple, responsive, and easy to interact with.

---

## 🛠 Tech Stack
- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Python, FastAPI
- **APIs:** AssemblyAI (STT), GeminiAI (LLM), Murf TTS API

---

## 🗺 Architecture
1. User speaks into the mic → Browser records audio  
2. Audio sent to backend → Processed via AssemblyAI STT  
3. Transcript sent to LLM API → Response generated  
4. Response converted to audio via TTS API  
5. Audio sent back to browser → Played for the user  

---

## ⚙️ Setup & Installation

### 1️⃣ Get the Project
Download the project folder from the source provided (ZIP file or local copy) and extract it to your desired location.

### 2️⃣ Set Environment Variables
Create a `.env` file in the backend folder with your API keys:

```env
MURF_API_KEY="Your API key here"
# Get your key from https://murf.ai/

GEMINI_API_KEY="Your API key here"
# Get your key from https://ai.google.dev

ASSEMBLYAI_API_KEY="Your API key here"
# Get your key from https://www.assemblyai.com/

### 3️⃣ Install Dependencies

If you have requirements.txt:

pip install -r requirements.txt

Or manually:

pip install fastapi uvicorn requests python-dotenv assemblyai openai

### 4️⃣ Start the Backend
uvicorn main:app --reload

### 5️⃣ Open the Frontend

Once your server is up and running navigate to 

https://localhost:8000





