# AI Voice Agent 🎙️

A conversational AI voice agent built with FastAPI that combines Speech-to-Text (STT), Large Language Models (LLM), and Text-to-Speech (TTS) technologies to create a seamless voice-based interaction experience.

## ✨ Features

- **Speech-to-Text**: Convert audio input to text using AssemblyAI
- **AI Conversations**: Intelligent responses powered by Google Gemini
- **Text-to-Speech**: Natural voice output using Murf AI
- **Session Management**: Persistent chat history for conversational context
- **Audio Processing**: Upload, transcribe, and generate audio files
- **RESTful API**: Clean, documented API endpoints
- **Error Handling**: Robust fallback mechanisms for service failures

## 🏗️ Architecture

```
voice-agent/
│
├── services/
│   ├── stt_service.py        # Speech-to-text logic (AssemblyAI)
│   ├── tts_service.py        # Text-to-speech logic (Murf AI)
│   └── llm_service.py        # LLM logic (Google Gemini)
│
├── static/                   # Frontend files
├── uploads/                  # Audio file uploads
├── main.py                   # FastAPI application
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables
└── README.md                 # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- API keys for:
  - [AssemblyAI](https://www.assemblyai.com/)
  - [Murf AI](https://murf.ai/)
  - [Google AI Studio](https://ai.google.dev/)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-voice-agent.git
cd ai-voice-agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file:
```env
MURF_API_KEY=your_murf_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
ASSEMBLYAI_API_KEY=your_assemblyai_api_key_here
```

4. Run the application:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## 📡 API Endpoints

### Core Endpoints

- `GET /` - Serve the main interface
- `GET /ping` - Health check
- `GET /health` - Comprehensive service health check

### Audio Processing

- `POST /upload-audio/` - Upload audio files
- `POST /transcribe/file` - Transcribe audio to text
- `POST /generate-audio/` - Generate speech from text
- `POST /tts-echo` - Echo transcribed audio as speech

### AI Interaction

- `POST /llm/query` - Single query processing (STT → LLM → TTS)
- `POST /agent/chat/{sessionId}` - Conversational chat with memory
- `GET /agent/chat/{sessionId}` - Retrieve chat history
- `DELETE /agent/chat/{sessionId}` - Clear chat history

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `MURF_API_KEY` | Murf AI API key for text-to-speech | Yes |
| `GEMINI_API_KEY` | Google Gemini API key for LLM | Yes |
| `ASSEMBLYAI_API_KEY` | AssemblyAI API key for speech-to-text | Yes |

### Service Configuration

- **Default TTS Voice**: `en-US-natalie`
- **Default LLM Model**: `gemini-2.5-flash`
- **Upload Directory**: `uploads/`
- **Max File Size**: 50MB

## 🛠️ Technologies Used

- **Backend**: FastAPI, Python
- **AI Services**: 
  - AssemblyAI (Speech-to-Text)
  - Google Gemini (Language Model)
  - Murf AI (Text-to-Speech)
- **Data Validation**: Pydantic
- **HTTP Client**: Requests
- **Environment Management**: python-dotenv

## 📝 Usage Examples

### Generate Audio from Text
```bash
curl -X POST "http://localhost:8000/generate-audio/" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, world!", "voice_id": "en-US-natalie"}'
```

### Start a Conversation
```bash
curl -X POST "http://localhost:8000/agent/chat/session123" \
  -F "file=@audio.wav"
```

## 🔒 Security Notes

- API keys are stored in environment variables
- CORS is currently set to allow all origins (⚠️ restrict for production)
- File uploads are stored locally (consider cloud storage for production)

## 🚧 Development

### Project Structure

The application follows a modular architecture:

- **Services Layer**: Encapsulates third-party API interactions
- **Models**: Pydantic schemas for request/response validation  
- **Routes**: FastAPI endpoints with proper error handling
- **Configuration**: Environment-based settings management

### Adding New Features

1. Create service classes in the `services/` directory
2. Define Pydantic models for data validation
3. Add routes in `main.py` with proper error handling
4. Update documentation and tests

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Support

For questions and support, please open an issue in the GitHub repository.

---

**30 Days of AI Voice Agents - Day 14** 🎯

*Part of the 30-day AI voice agent development challenge. This project demonstrates clean architecture, service separation, and production-ready code practices.*