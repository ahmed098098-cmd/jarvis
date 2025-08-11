"""
Jarvis — All-in-one assistant (single-file)

Features:
- Speech recognition (SpeechRecognition + PyAudio)
- Text-to-speech (Windows SAPI)
- ChatterBot fallback chat
- Local Pakistan knowledge base (history, geography, facts)
- Wikipedia summary fallback (online)
- Time / Date / Day commands
- Independence Day (Aug 14) automatic alert
- System controls (shutdown, restart, abort, lock, sleep, logoff, taskmgr, cmd, control panel)
- Open apps & websites (Chrome, YouTube, WhatsApp, VS Code, Settings, Calculator)
- Write application templates to Notepad by spoken title
- Play music from a folder
- Reminders + background checker
- Persistent memory (name, reminders, chat history)
"""

import os
import json
import subprocess
import webbrowser
import random
import time
import datetime
import threading
import warnings

# 3rd-party libs
import speech_recognition as sr
import wikipedia
import win32com.client

# Optional: chatterbot (can be heavy). If not installed, code falls back safely.
try:
    from chatterbot import ChatBot
    from chatterbot.trainers import ListTrainer
    CHATBOT_AVAILABLE = True
except Exception:
    CHATBOT_AVAILABLE = False

# ---- User configuration ----
MUSIC_FOLDER = r"C:\Users\sdoco"            # <-- change to your music folder
VSCODE_PATH = r"C:\Users\sdoco\AppData\Local\Programs\Microsoft VS Code\Code.exe"  # change if needed
OPENWEATHER_API_KEY = ""   # optional: set to use weather feature
WEATHER_CITY = "Islamabad" # optional: city for weather
LISTEN_TIMEOUT = 5         # seconds phrase_time_limit
MEMORY_FILE = "jarvis_memory.json"
# ----------------------------

# Suppress wikipedia parser warning (cosmetic)
warnings.filterwarnings("ignore", category=UserWarning, module='wikipedia')

# Initialize TTS
speaker = win32com.client.Dispatch("SAPI.SpVoice")

def speak(text):
    """Speak and print."""
    if not text:
        return
    print("Jarvis:", text)
    try:
        speaker.Speak(text)
    except Exception:
        # If TTS fails, just print
        pass

def listen(timeout=LISTEN_TIMEOUT):
    """Listen from microphone and return lowercase text (or empty string)."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        # optional energy threshold — you may tune this
        r.energy_threshold = 300
        try:
            audio = r.listen(source, phrase_time_limit=timeout)
        except Exception as e:
            print("Microphone listening error:", e)
            return ""
    try:
        query = r.recognize_google(audio)
        print("You:", query)
        return query.lower()
    except sr.UnknownValueError:
        return ""
    except sr.RequestError:
        # network error for Google recognizer
        return ""

# Persistent memory
memory = {"name": None, "chat_history": [], "reminders": [], "last_independence_year": 0}
if os.path.exists(MEMORY_FILE):
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            memory.update(json.load(f))
    except Exception:
        pass

def save_memory():
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(memory, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print("Could not save memory:", e)

# Initialize ChatterBot if available
if CHATBOT_AVAILABLE:
    bot = ChatBot('Jarvis', storage_adapter='chatterbot.storage.SQLStorageAdapter')
    trainer = ListTrainer(bot)
    try:
        trainer.train([
            "hello", "Hello! I am Jarvis, your assistant.",
            "how are you", "I am fine, thank you!",
            "what is your name", "My name is Jarvis.",
            "who created you", "You did — an awesome developer."
        ])
    except Exception:
        pass

# ---------------- Pakistan knowledge base (more detail can be added) ---------------
pakistan_info = {
    "capital": "Islamabad is the capital city of Pakistan. It was built during the 1960s to replace Karachi as the capital.",
    "largest city": "Karachi is the largest city of Pakistan and the country's main seaport and financial centre.",
    "official language": "Urdu is the national language and lingua franca; English is an official language used in government and business. Many regional languages are spoken such as Punjabi, Sindhi, Pashto and Balochi.",
    "currency": "Pakistani Rupee (PKR) is the currency of Pakistan.",
    "population": "Pakistan's population is over 240 million (estimates vary by year), making it one of the world's most populous countries.",
    "independence day": "Pakistan gained independence from British rule on 14 August 1947. Independence Day is celebrated every year on August 14.",
    "geography": (
        "Pakistan is in South Asia, bordered by India to the east, Afghanistan and Iran to the west, "
        "China to the north, and the Arabian Sea to the south. It has varied geography: coastal areas, "
        "plains, deserts, and high mountain ranges. Northern Pakistan contains some of the world's highest peaks, including K2."
    ),
    "history": (
        "Modern Pakistan was created at the partition of British India in 1947 as a state for Muslims of the subcontinent. "
        "Key milestones:\n"
        "- Prehistory & ancient: The Indus Valley Civilization (c. 2600–1900 BCE) flourished in parts of present-day Pakistan.\n"
        "- Persian, Greek, Mauryan, Kushan and Islamic empires influenced the region.\n"
        "- Medieval: Arrival of Islam, Ghaznavids, Ghurids, Delhi Sultanate, Mughal Empire.\n"
        "- British era: The region became part of British India (19th – 20th centuries).\n"
        "- 1947: Partition led to creation of Pakistan under Muhammad Ali Jinnah (Quaid-e-Azam).\n"
        "- 1947–1971: Pakistan comprised West and East wings; East Pakistan became Bangladesh after the 1971 Liberation War.\n"
        "- Since independence, Pakistan has alternated between civilian rule and military governments, developed industry and agriculture, "
        "and faces challenges like governance, security and economic development."
    ),
    "province list": "Pakistan's provinces include Punjab, Sindh, Khyber Pakhtunkhwa (KP), Balochistan; federal territories include Islamabad Capital Territory and regions such as Gilgit-Baltistan and Azad Jammu & Kashmir.",
    "national animal": "The markhor is the national animal of Pakistan.",
    "national bird": "The chukar partridge is often recognized as a national bird symbol.",
    "national flower": "Jasmine is considered a national flower/flower emblem in Pakistan."
}
# -------------------------------------------------------------------------------

# ---------------- Helper utilities ------------------------------------------------
def get_pakistan_answer(query):
    """Return an offline Pakistan fact if any key matches the query."""
    q = query.lower()
    for key, text in pakistan_info.items():
        if key in q:
            return text
    # also check some common question forms
    if "capital of pakistan" in q or "what is the capital of pakistan" in q:
        return pakistan_info.get("capital")
    if "founder" in q or "who founded" in q or "quaid" in q:
        return "Pakistan's founder (Quaid-e-Azam) was Muhammad Ali Jinnah."
    if "k2" in q or "highest mountain" in q or "highest peak" in q:
        return "K2 (Mount Godwin-Austen) is the highest peak in Pakistan and the second highest in the world."
    return None

def get_time_text():
    now = datetime.datetime.now()
    return now.strftime("The time is %I:%M %p")

def get_date_text():
    now = datetime.datetime.now()
    return now.strftime("Today is %A, %d %B %Y")

def is_independence_day_today():
    now = datetime.date.today()
    return now.month == 8 and now.day == 14

# Wikipedia summary (safe wrapper)
def wiki_summary(query, sentences=2):
    try:
        # clean common prefixes
        q = query.lower()
        for prefix in ["tell me about", "who is", "what is", "what are", "define", "explain"]:
            q = q.replace(prefix, "")
        q = q.strip()
        if not q:
            return None
        wikipedia.set_lang("en")
        return wikipedia.summary(q, sentences=sentences, auto_suggest=True)
    except Exception as e:
        # print("Wikipedia error:", e)
        return None

# ---------------- System and app controls ---------------------------------------
def open_chrome(url="https://www.google.com"):
    try:
        webbrowser.open(url)
        speak(f"Opening Chrome with {url}")
    except Exception as e:
        speak(f"Failed to open browser: {e}")

def open_youtube(query=None):
    url = "https://www.youtube.com"
    if query:
        url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
    open_chrome(url)

def open_whatsapp():
    open_chrome("https://web.whatsapp.com")

def open_settings():
    try:
        subprocess.Popen("start ms-settings:", shell=True)
        speak("Opening Settings.")
    except Exception as e:
        speak("Could not open Settings: " + str(e))

def open_vscode():
    try:
        if os.path.exists(VSCODE_PATH):
            subprocess.Popen([VSCODE_PATH])
            speak("Opening Visual Studio Code.")
        else:
            speak("VS Code not found at configured path.")
    except Exception as e:
        speak("Could not open VS Code: " + str(e))

def open_calculator():
    try:
        subprocess.Popen("calc.exe")
        speak("Opening Calculator.")
    except Exception as e:
        speak("Could not open Calculator: " + str(e))

def open_task_manager():
    try:
        subprocess.Popen("taskmgr")
        speak("Opening Task Manager.")
    except Exception as e:
        speak("Could not open Task Manager: " + str(e))

def open_cmd():
    try:
        subprocess.Popen("start cmd", shell=True)
        speak("Opening Command Prompt.")
    except Exception as e:
        speak("Could not open Command Prompt: " + str(e))

def open_control_panel():
    try:
        subprocess.Popen("control")
        speak("Opening Control Panel.")
    except Exception as e:
        speak("Could not open Control Panel: " + str(e))

def system_shutdown(delay_seconds=60):
    speak(f"Shutting down the system in {delay_seconds} seconds.")
    os.system(f"shutdown /s /t {delay_seconds}")

def system_restart(delay_seconds=60):
    speak(f"Restarting the system in {delay_seconds} seconds.")
    os.system(f"shutdown /r /t {delay_seconds}")

def system_abort():
    speak("Aborting shutdown/restart.")
    os.system("shutdown /a")

def lock_workstation():
    try:
        os.system("rundll32.exe user32.dll,LockWorkStation")
        speak("Locking the workstation.")
    except Exception as e:
        speak("Could not lock workstation: " + str(e))

def sleep_system():
    try:
        # may require privileges
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        speak("Putting system to sleep.")
    except Exception as e:
        speak("Could not put system to sleep: " + str(e))

def logoff():
    try:
        os.system("shutdown /l")
    except Exception as e:
        speak("Could not log off: " + str(e))

# ---------------- Notes / Applications / Music ----------------------------------
def write_in_notepad(text, filename="jarvis_note.txt"):
    try:
        path = os.path.abspath(filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        subprocess.Popen(["notepad.exe", path])
        speak("Opened Notepad with requested content.")
    except Exception as e:
        speak("Could not write to Notepad: " + str(e))

# very simple app templates
APP_TEMPLATES = {
    "calculator": """# Simple calculator
def add(a,b): return a+b
def sub(a,b): return a-b
def mul(a,b): return a*b
def div(a,b): return a/b if b!=0 else None

if __name__ == '__main__':
    print('Calculator - enter "exit" to quit')
    while True:
        expr = input('Enter expression: ')
        if expr.strip().lower() == 'exit':
            break
        try:
            print(eval(expr))
        except Exception as e:
            print('Error:', e)
""",
    "todo": """# Simple TODO app
tasks=[]
while True:
    cmd=input('add/show/exit: ').strip().lower()
    if cmd=='add':
        t=input('Task: ')
        tasks.append(t)
    elif cmd=='show':
        for i,t in enumerate(tasks,1):
            print(i,t)
    elif cmd=='exit':
        break
""",
    "vs code": f"""# VS Code launcher
import os
os.system(r'{VSCODE_PATH}')
"""
}

def create_application_from_title(title):
    key = title.lower().strip()
    # try to find a matching template key
    for k in APP_TEMPLATES:
        if k in key:
            write_in_notepad(APP_TEMPLATES[k], filename=f"{k}_template.py")
            return True
    # fallback: create placeholder template
    placeholder = f"# Application: {title}\nprint('This is a placeholder for {title}')\n"
    write_in_notepad(placeholder, filename=f"{key.replace(' ','_')[:50]}.py")
    return True

def play_random_music():
    try:
        files = []
        for root, _, filenames in os.walk(MUSIC_FOLDER):
            for fn in filenames:
                if fn.lower().endswith((".mp3", ".wav")):
                    files.append(os.path.join(root, fn))
        if not files:
            speak("No music files found in your configured music folder.")
            return
        song = random.choice(files)
        speak(f"Playing {os.path.basename(song)}")
        os.startfile(song)
    except Exception as e:
        speak("Could not play music: " + str(e))

# ---------------- Reminders & Independence Day ----------------------------------
def add_reminder(text, time_str=None):
    """time_str optional in HH:MM 24-hour format for daily check."""
    rem = {"text": text, "time": time_str}
    memory.setdefault("reminders", []).append(rem)
    save_memory()
    speak(f"Reminder added: {text} at {time_str if time_str else 'no specific time'}")

def check_reminders_loop():
    """Background thread that checks reminders every 60 seconds."""
    while True:
        now = datetime.datetime.now().strftime("%H:%M")
        # independence day alert once per year
        today = datetime.date.today()
        if today.month == 8 and today.day == 14:
            last_year = memory.get("last_independence_year", 0)
            if last_year != today.year:
                speak("Happy Independence Day! Today is 14th August — Pakistan's Independence Day.")
                memory["last_independence_year"] = today.year
                save_memory()
        # time-based reminders
        for rem in list(memory.get("reminders", [])):
            if rem.get("time") == now:
                speak("Reminder: " + rem.get("text", ""))
                # remove one-time reminder (keep if you want recurring)
                try:
                    memory["reminders"].remove(rem)
                    save_memory()
                except ValueError:
                    pass
        time.sleep(60)

# start reminder thread
reminder_thread = threading.Thread(target=check_reminders_loop, daemon=True)
reminder_thread.start()

# ---------------- Command handling ---------------------------------------------
def handle_query(query):
    """Central command parser. Returns a text response (may be None if action already speaks)."""
    q = query.lower()

    # quick exits
    if any(x in q for x in ["exit", "quit", "bye", "goodbye"]):
        return "exit"

    # Time / date / day (handle early)
    if "time" in q and "what" in q or q.strip() in ("time", "what time is it", "tell me the time"):
        return get_time_text()
    if "date" in q or "day" in q or "what day" in q or "what is the date" in q:
        return get_date_text()

    # Independence day check request
    if "independence day" in q or "14 august" in q or "august 14" in q:
        return "Pakistan's Independence Day is on 14 August. Pakistan became independent on 14 August 1947."

    # Pakistan knowledge offline
    if "pakistan" in q or any(k in q for k in ["capital of pakistan", "history of pakistan", "pakistan geography", "founder of pakistan", "k2", "karachi", "islamabad"]):
        ans = get_pakistan_answer(q)
        if ans:
            return ans
        # fallback to general Pakistan summary
        return pakistan_info.get("history")  # or more general text

    # Weather (optional using OpenWeather)
    if "weather" in q:
        if OPENWEATHER_API_KEY:
            try:
                import requests
                url = f"http://api.openweathermap.org/data/2.5/weather?q={WEATHER_CITY}&appid={OPENWEATHER_API_KEY}&units=metric"
                r = requests.get(url, timeout=8)
                data = r.json()
                if data.get("cod") == 200:
                    desc = data["weather"][0]["description"]
                    temp = data["main"]["temp"]
                    hum = data["main"]["humidity"]
                    return f"The weather in {WEATHER_CITY} is {desc}, temperature {temp}°C, humidity {hum}%."
                else:
                    return "Sorry, I couldn't fetch weather now."
            except Exception:
                return "Weather check failed (network or API error)."
        else:
            return "Weather is not configured. Please add your OpenWeatherMap API key in the script to enable weather."

    # Open apps and websites
    if "open chrome" in q or (q.strip() == "chrome"):
        open_chrome()
        return "Opened Chrome."
    if "open youtube" in q:
        # optionally: "open youtube for cats"
        if "for" in q:
            parts = q.split("for", 1)
            open_youtube(parts[1].strip())
        else:
            open_youtube()
        return "Opened YouTube."
    if "open whatsapp" in q or "whatsapp" in q:
        open_whatsapp()
        return "Opened WhatsApp Web."
    if "open settings" in q or "settings" in q:
        open_settings()
        return "Opened Settings."
    if "open vscode" in q or "open visual studio code" in q or "vs code" in q:
        open_vscode()
        return "Opening VS Code."
    if "open calculator" in q or "calculator" in q:
        open_calculator()
        return "Calculator opened."
    if "task manager" in q:
        open_task_manager()
        return "Task Manager opened."
    if "command prompt" in q or q.strip() == "cmd":
        open_cmd()
        return "Command Prompt opened."
    if "control panel" in q:
        open_control_panel()
        return "Control Panel opened."

    # System controls
    if "shutdown" in q and "abort" not in q and "cancel" not in q:
        system_shutdown(60)
        return "Shutdown scheduled in 60 seconds."
    if "restart" in q:
        system_restart(60)
        return "Restart scheduled in 60 seconds."
    if "abort shutdown" in q or "cancel shutdown" in q or "abort restart" in q:
        system_abort()
        return "Shutdown/restart aborted."
    if "lock" in q and "workstation" not in q:
        lock_workstation()
        return "Workstation locked."
    if "sleep" in q:
        sleep_system()
        return "System sleep attempted."
    if "log off" in q or "logoff" in q:
        logoff()
        return "Logoff initiated."

    # Music
    if "play music" in q or q.strip() == "music":
        play_random_music()
        return "Playing music."

    # Write app/document/note
    if "write application" in q or "create application" in q or ("write" in q and "application" in q):
        # prompt for title externally (handled in main loop)
        return "prompt_application_title"
    if any(x in q for x in ["write note", "write a note", "write essay", "write letter"]):
        return "prompt_write_text"

    # Reminders
    if "remind me to" in q:
        # e.g. 'remind me to call david at 18:00'
        try:
            after = q.split("remind me to", 1)[1].strip()
            # naive: if 'at HH:MM' present
            if " at " in after:
                text, tstr = after.rsplit(" at ", 1)
                # validate HH:MM
                try:
                    datetime.datetime.strptime(tstr.strip(), "%H:%M")
                    add_reminder(text.strip(), tstr.strip())
                    return f"Reminder set for {tstr.strip()}: {text.strip()}"
                except Exception:
                    add_reminder(after.strip(), None)
                    return "Reminder added without specific time (time format invalid)."
            else:
                add_reminder(after.strip(), None)
                return "Reminder added without time."
        except Exception:
            return "Sorry, I couldn't parse the reminder."

    # Get stored name
    if "what is my name" in q or "what's my name" in q:
        if memory.get("name"):
            return f"Your name is {memory['name']}."
        return "I don't know your name yet. Tell me 'my name is ...' to save it."

    if q.startswith("my name is "):
        name = q.replace("my name is", "").strip()
        if name:
            memory["name"] = name
            save_memory()
            return f"Nice to meet you, {name}. I will remember your name."
        else:
            return "I did not catch your name."

    # Wikipedia Q/A (only after we've considered other conditions)
    if any(word in q for word in ["who", "what", "when", "where", "why", "how", "tell me about", "define", "explain"]):
        w = wiki_summary(q, sentences=2)
        if w:
            return w
        # else fallback to chatbot below

    # Fallback to ChatterBot if available
    if CHATBOT_AVAILABLE:
        try:
            reply = bot.get_response(q)
            return str(reply)
        except Exception:
            pass

    # Ultimate fallback
    return "Sorry, I don't understand that yet. Try asking another way."

# ---------------- Main loop -----------------------------------------------------
def main_loop():
    speak("Jarvis starting up.")
    # greet
    if memory.get("name"):
        speak(f"Welcome back, {memory['name']}!")
    else:
        speak("Hello! What's your name?")
        nm = listen(timeout=6)
        if nm:
            memory["name"] = nm
            save_memory()
            speak(f"Nice to meet you, {nm}!")

    # Independence Day immediate check
    if is_independence_day_today():
        today = datetime.date.today()
        last = memory.get("last_independence_year", 0)
        if last != today.year:
            speak("Happy Independence Day! Today is 14th August, Pakistan's Independence Day.")
            memory["last_independence_year"] = today.year
            save_memory()

    speak("How can I assist you today?")

    while True:
        speak("Please say your command.")
        q = listen(timeout=8)
        if not q:
            speak("I didn't catch that. Say please type your command.")
            # allow typed fallback
            try:
                typed = input("Type command (or press Enter to skip): ").strip()
            except Exception:
                typed = ""
            if not typed:
                continue
            q = typed.lower()

        result = handle_query(q)

        if result == "exit":
            speak("Goodbye! Have a great day.")
            break

        # special prompts from handle_query
        if result == "prompt_application_title":
            speak("Please tell me the application title.")
            title = listen(timeout=8)
            if not title:
                speak("I did not catch the title. Please type the application title:")
                title = input("Application title: ").strip()
            if title:
                create_application_from_title(title)
                speak(f"Created application template for {title} in Notepad.")
            else:
                speak("No title provided. Cancelled.")
            continue

        if result == "prompt_write_text":
            speak("What should I write?")
            body = listen(timeout=12)
            if not body:
                speak("I did not catch the text. Please type the text to write:")
                body = input("Text: ").strip()
            if body:
                write_in_notepad(body)
                speak("Written to Notepad.")
            else:
                speak("No text provided. Cancelled.")
            continue

        # Normal textual response
        if result:
            speak(result)
        time.sleep(0.5)

if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        print("Exiting Jarvis.")
    except Exception as e:
        print("Jarvis crashed:", e)