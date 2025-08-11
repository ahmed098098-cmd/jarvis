

Jarvis: Your All-in-One Voice Assistant (Single File)


Jarvis is a powerful, lightweight, and extensible voice assistant built entirely in a single Python file. Designed for Windows, it combines speech recognition and text-to-speech capabilities to offer a wide range of features, from system automation to personalized reminders and a local knowledge base.

This project is perfect for developers who want a ready-to-go personal assistant or a solid foundation to build their own custom voice-controlled applications.

Key Features
🎙️ Voice-Activated Interface: Interact naturally using your voice with both speech recognition and text-to-speech (TTS) via SpeechRecognition and Windows SAPI.

🌍 Intelligent Fallbacks: When local knowledge isn't enough, Jarvis can intelligently pull summaries from Wikipedia to answer your questions.

🇵🇰 Localized Knowledge Base: Get instant, offline answers about Pakistan's history, geography, and facts. A special alert is also included for Pakistan's Independence Day (August 14th).

🤖 Smart Conversational Abilities: Features a fallback ChatterBot integration for more human-like conversations, ensuring a response even for general queries.

⏰ Reminders & Persistent Memory: Set reminders that are checked in the background. The assistant remembers your name and chat history across sessions.

💻 System & App Control: Effortlessly manage your computer with voice commands to:

Open apps and websites (Chrome, YouTube, WhatsApp, VS Code, Calculator, Settings).

Control system functions like shutdown, restart, lock, sleep, and logoff.

Access Task Manager, Command Prompt, and Control Panel.

🎵 Media Playback: Automatically plays a random music file from a specified folder with a simple voice command.

✍️ Dynamic Code & Document Generation: Speak a title and Jarvis will open Notepad with a pre-written template for common applications (e.g., calculator, to-do list) or a blank note for you to write in.

How It Works
Jarvis uses several key Python libraries to achieve its functionality:

SpeechRecognition and PyAudio handle the conversion of spoken words to text.

win32com.client leverages the Windows SAPI to provide clear text-to-speech.

wikipedia is used for online knowledge queries.

chatterbot provides a simple conversational AI layer (optional, but recommended).

The project's single-file structure makes it easy to understand, modify, and run. With minimal configuration, you can have your own voice assistant up and running in minutes.

Getting Started
To get started with your own Jarvis assistant, follow these simple steps:

Clone this repository or download the jarvis.py file.

Install the required libraries:

CMD
pip install SpeechRecognition wikipedia PyAudio
Optional: For conversational features, install ChatterBot:

CMD
pip install chatterbot chatterbot_corpus
Open the script and configure the User Configuration section with your preferred paths and optional API keys.

Run the script:

CMD
python jarvis.py
You're all set! Just say "Hey Jarvis" or simply speak your command when prompted.
