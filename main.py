import os
import requests
import sounddevice as sd
import scipy.io.wavfile as wav
import speech_recognition as sr
import numpy as np
import wikipedia
import openai
import tempfile
import googleapiclient.discovery

# === OpenRouter settings ===
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_API_KEY = "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"
MODEL = "mistralai/mistral-7b-instruct"

# === Google Search API setup ===
GOOGLE_API_KEY = "AIzaSyDhydRyrhrBn5WMQVNHbMGhEvIIHlvgs0E"
CX = "12a66b45e33b941cd"

# === OpenAI for reasoning & detailed insights ===
openai.api_key = "YOUR_OPENAI_API_KEY"

def record_until_enter(fs=44100):
    print("\n🎙️ Press [Enter] to START recording.")
    input()
    print("🟢 Recording... Speak now.")

    audio_data = []

    def callback(indata, frames, time, status):
        audio_data.append(indata.copy())

    with sd.InputStream(samplerate=fs, channels=1, callback=callback):
        input("⏹️ Press [Enter] again to STOP recording.\n")

    print("🔄 Processing audio...")
    audio_array = np.concatenate(audio_data, axis=0)
    int_audio = np.int16(audio_array * 32767)
    temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    wav.write(temp_wav.name, fs, int_audio)
    return temp_wav.name

def speech_to_text(filename):
    recognizer = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        audio = recognizer.record(source)
    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return "[Couldn't understand speech]"
    except sr.RequestError:
        return "[Speech recognition failed]"

def web_search(query):
    service = googleapiclient.discovery.build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
    res = service.cse().list(q=query, cx=CX, num=3).execute()
    if "items" in res:
        output = ""
        for i, item in enumerate(res["items"], 1):
            title = item.get("title")
            snippet = item.get("snippet")
            link = item.get("link")
            output += f"\n[{i}] {title}\n{snippet}\n🔗 {link}\n\n"
        return output.strip()
    return " No search results found."

def ask_openrouter(prompt):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are Octa, an AI assistant that responds with kindness, emotional intelligence, "
                    "spiritual wisdom, and physical/health advice. You are great at answering educational "
                    "questions for students in Nigeria. Give detailed, well-structured answers with examples."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    try:
        response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return f"[OpenRouter error {response.status_code}: {response.text}]"
    except Exception as e:
        return f"[Request failed: {e}]"

def get_educational_insight(topic):
    try:
        summary = wikipedia.summary(topic, sentences=5)  # More than 3 sentences
        return summary
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Topic unclear. Did you mean one of these?\n{', '.join(e.options[:5])}..."
    except wikipedia.exceptions.PageError:
        return "No matching Wikipedia page found."

def main():
    print("👋 Hi! I’m Octa — your smart assistant.")
    print("Choose a mode to continue:")

    while True:
        try:
            mode = input("\nChoose mode:\n1. 🎙️ Voice input\n2. 📝 Text input\n3. 🔍 Web Search\n4. 🧠 Reasoning\n5. 📚 Educational Insight\n6. ❌ Exit\n> ")

            if mode == "1":
                audio_file = record_until_enter()
                user_input = speech_to_text(audio_file)
                os.remove(audio_file)
                print(f"\n🗣️ You said: {user_input}")
                response = ask_openrouter(user_input)
                print(f"\n🤖 [Octa]: {response}")

            elif mode == "2":
                user_input = input("\nEnter your question: ")
                if user_input.lower() in ['bye', 'exit', 'quit']:
                    print("👋 [Octa]: Goodbye!")
                    break
                response = ask_openrouter(user_input)
                print(f"\n🤖 [Octa]: {response}")

            elif mode == "3":
                query = input("\nEnter web search topic: ")
                result = web_search(query)
                print(f"\n🔍 Web Result: {result}")

            elif mode == "4":
                prompt = input("\nEnter topic for reasoning: ")
                response = ask_openrouter(prompt)
                print(f"\n🧠 Reasoning: {response}")

            elif mode == "5":
                topic = input("\nEnter topic for detailed insight: ")
                insight = get_educational_insight(topic)
                print(f"\n📚 Insight: {insight}")

            elif mode == "6":
                print("👋 [Octa]: Goodbye!")
                break

            else:
                print("⚠️ Invalid option. Please choose again.")

        except KeyboardInterrupt:
            print("\n[Octa]: Session ended. Bye!")
            break

if __name__ == "__main__":
    main()
