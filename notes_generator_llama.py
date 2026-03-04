from urllib import response

import requests
import json
# from google import genai
# from openai import OpenAI
import os
# from huggingface_hub import InferenceClient

# client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# client = InferenceClient(token=os.getenv("HF_API_KEY"))

def chunk_text(text, chunk_size=3000):  # Smaller chunks for local models
    """Split text into smaller chunks for processing"""
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

# ================= OLLAMA HELPER =================
def call_ollama(prompt, model="qwen2.5:7b",max_tokens=400):
    """Send prompt to local Ollama instance"""
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": prompt,  # Now expects a list of messages
                "stream": False,
                "options": {
                    "temperature": 0.8,
                    "num_predict": max_tokens,  # Enough tokens for eval + question
                }
            },
            timeout=180
        )
        
        # Check if request was successful
        response.raise_for_status()
        
        # Parse JSON response
        result = response.json()
        
        return result["response"]
        
    except requests.exceptions.ConnectionError:
        return "❌ Error: Cannot connect to Ollama. Make sure it's running:\n\n`ollama serve`"
    except requests.exceptions.Timeout:
        return "❌ Error: Request timed out. The model might be too slow for your CPU."
    except Exception as e:
        return f"❌ Error: {str(e)}"

# ================= 1️⃣ LECTURE NOTES =================
def generate_notes(transcript):
    chunks = chunk_text(transcript, chunk_size=3000)  # Adjust chunk size for local models
    full_notes = ""

    for chunk in chunks:
        prompt = f"""
        Convert the following lecture transcript into:

        - Clear structured headings
        - Bullet points
        - Key concepts
        - Important takeaways
        - Exam-ready summary

        Keep the notes concise, organized, and easy to review. Use markdown formatting for headings and lists.
        About the Subject componets and the grading criteria, keep it absolutely brief and to the point. Avoid unnecessary elaboration.
        The highlight should be on clarity of the topic that is present in the transcript. The notes should be structured in a way that makes it easy for students to quickly grasp the main ideas and concepts without having to read through lengthy explanations.

        Transcript:
        {chunk}
        """
        result = call_ollama(prompt, model="qwen2.5:1.5b")

    full_notes += result + "\n\n"

    return full_notes

# ================= 2️⃣ ASK TOPIC =================
def generate_topic_explanation(topic):
    prompt = f"""
You are an academic educator.

The user has asked about the topic: "{topic}".

If the term has multiple meanings, choose the most academically relevant interpretation 
(commonly taught in schools or universities).

Provide a clear and structured explanation suitable for a general audience.

Structure your response as:

1. Definition (simple and clear)
2. Core Concept / Theory
3. Simple Example
4. Real-world Applications
5. Key Points for Exams or Interviews

Avoid informal interpretations unless explicitly requested.
"""

    return call_ollama(prompt)


# ================= 4️⃣ VIVA CHATBOT =================
# def viva_chatbot(subject, chat_history):
#     prompt = prompt = f"""
# You are a strict academic viva examiner.

# The subject of the viva is: "{subject}"

# Your task is to conduct a real interactive oral (interview focused based on the subject solely) exam.

# Important Instructions:
# - Ask ONLY ONE question at a time.
# - Do NOT give long explanations.
# - Wait for the student's response.
# - After each answer:
#     1. Briefly evaluate the answer (2–3 lines max).
#     2. Breifly explain the correct answer if the student's answer was wrong (2–3 lines max).
#     3. Ask a deeper, conceptual follow-up question based on the student's answer.
# - Increase difficulty gradually.
# - Be concise.
# - Test the student's understanding, concepts and problem-solving skills, not just definitions.

# If this is the beginning (no prior conversation), start with a basic conceptual question, do not ask about the detals of the student or their background. Focus solely on the subject matter.
# Always end by asking a question, never by giving an explanation. The conversation should be driven by the student's answers.
# Conversation so far:
# {chat_history}
# """
#     return call_ollama(prompt, model="qwen2.5:1.5b")

def viva_chatbot(subject, user_input=None):
    """
    Stable viva chatbot (no raw history dumping)
    """


    if user_input is None:
        # First question
        prompt = f"""
You are a strict viva examiner for {subject}.

Ask ONE basic conceptual question to begin the exam.

Do NOT include introductions.
Do NOT say "Certainly", "Here is", or similar phrases.
Output ONLY the question.
The response must contain only one question ending with a question mark.
"""

    else:
        prompt = f"""You are a viva examiner testing a student on {subject}.

Student's Answer: "{user_input}"

Your task:
1. EVALUATION (2-3 sentences): Is the answer correct? What's missing?
2. FOLLOW-UP QUESTION: Ask ONE harder question based on their answer.

Format your response exactly like this:

**Evaluation:** <2-3 sentence evaluation>

**Follow-up Question:** <one deeper question ending with a question mark>"""

    return call_ollama(prompt, model="qwen2.5:3b")