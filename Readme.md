# Notesy AI 📚🤖

**Notesy AI** is an AI-powered academic assistant designed to transform lecture transcripts into structured study materials.  
The system uses Large Language Models (LLMs) to generate organized notes, explain academic topics, and simulate viva-style questioning for exam preparation.


## Features

- **Lecture-to-Notes Generation**
  - Converts raw lecture transcripts into structured, exam-ready notes.

-  **Topic Explanation**
  - Generates clear academic explanations for user-entered topics.

-  **Viva Chatbot**
  - Conducts interactive oral exam-style questioning.

-  **PDF Export**
  - Generated notes can be downloaded as a formatted PDF.

-  **Custom UI**
  - Built using Streamlit with theme support and intuitive navigation.


##  System Architecture

User Input  
↓  
Streamlit Web Application  
↓  
Text Preprocessing (Chunking)  
↓  
LLM Processing (Local / Cloud Models)  
↓  
Structured Output (Notes / Explanation / Viva Chat)  
↓  
PDF Export


##  Technologies Used

- **Python**
- **Streamlit** – Web Application Framework
- **Ollama** – Local LLM Inference
- **Gemini API** – Cloud LLM (optional configuration)
- **Whisper** – Speech-to-Text Prototype
- **FPDF** – PDF generation
- **JSON** – Data handling
- **HTTP Requests** – Local model communication


##  Algorithms Implemented

### Notes Generation
- Transcript chunking
- Prompt engineering
- LLM-based structured summarization

### Topic Explanation
- Academic disambiguation prompts
- Context-aware explanation generation

### Viva Chatbot
- Iterative Q&A loop
- Context evaluation
- Difficulty escalation logic



##  Speech-to-Text Module

A speech-to-text prototype using **OpenAI Whisper** was implemented and tested in **Google Colab with GPU acceleration**.

Due to hardware constraints for local inference, the current application processes **lecture transcripts (.txt files)** instead of raw audio input.  
The speech-to-text module remains a validated prototype for future integration.

##  Project Structure

notesy-ai/
│
├── notesy.py
├── notes_generator.py
├── speech.py
├── users.json
├── history.json
├── requirements.txt
└── README.md



##  How to Run

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Local Model Setup (Ollama)

This project uses local LLMs through **Ollama**.

Install Ollama:
https://ollama.com

Then pull the required models:
ollama pull qwen2.5:7b
ollama pull neural-chat:7b

Start the Ollama server:
ollama serve

Then run the Streamlit app:
streamlit run notesy.py


### Future Improvements
Real-time audio lecture transcription
Cloud-based AI deployment
User authentication & cloud note storage
Multi-language support
AI-based viva performance scoring
