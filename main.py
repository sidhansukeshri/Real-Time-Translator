import os
import threading
import tkinter as tk
from gtts import gTTS
from tkinter import ttk
import speech_recognition as sr
from playsound import playsound
from deep_translator import GoogleTranslator
from google.transliteration import transliterate_text

# Create an instance of Tkinter frame or window
win = tk.Tk()

# Set the geometry of tkinter frame
win.geometry("700x450")
win.title("Real-Time Voice🎙️ Translator🔊")
icon = tk.PhotoImage(file="icon.png")
win.iconphoto(False, icon)

# Create labels and text boxes for the recognized and translated text
input_label = tk.Label(win, text="Recognized Text ⮯")
input_label.pack()
input_text = tk.Text(win, height=5, width=50)
input_text.pack()

output_label = tk.Label(win, text="Translated Text ⮯")
output_label.pack()
output_text = tk.Text(win, height=5, width=50)
output_text.pack()

blank_space = tk.Label(win, text="")  # For spacing
blank_space.pack()

# Create a dictionary of language names and codes
language_codes = {
    "English": "en",
    "Hindi": "hi",
    "Bengali": "bn",
    "Spanish": "es",
    "Chinese (Simplified)": "zh-CN",
    "Russian": "ru",
    "Japanese": "ja",
    "Korean": "ko",
    "German": "de",
    "French": "fr",
    "Tamil": "ta",
    "Telugu": "te",
    "Kannada": "kn",
    "Gujarati": "gu",
    "Punjabi": "pa"
}

language_names = list(language_codes.keys())

# Create dropdown menus for the input and output languages
input_lang_label = tk.Label(win, text="Select Input Language:")
input_lang_label.pack()

input_lang = ttk.Combobox(win, values=language_names)
def update_input_lang_code(event):
    selected_language_name = event.widget.get()
    selected_language_code = language_codes[selected_language_name]
    input_lang.set(selected_language_code)
input_lang.bind("<<ComboboxSelected>>", lambda e: update_input_lang_code(e))
if input_lang.get() == "": input_lang.set("auto")
input_lang.pack()

down_arrow = tk.Label(win, text="▼")
down_arrow.pack()

output_lang_label = tk.Label(win, text="Select Output Language:")
output_lang_label.pack()

output_lang = ttk.Combobox(win, values=language_names)
def update_output_lang_code(event):
    selected_language_name = event.widget.get()
    selected_language_code = language_codes[selected_language_name]
    output_lang.set(selected_language_code)
output_lang.bind("<<ComboboxSelected>>", lambda e: update_output_lang_code(e))
if output_lang.get() == "": output_lang.set("en")
output_lang.pack()

blank_space = tk.Label(win, text="")  # For spacing
blank_space.pack()

# Flags and variables
keep_running = False
current_input_lang = "auto"
current_output_lang = "en"
language_change_flag = False  # Flag to track language changes

# Threading-safe language update function
def update_language_settings():
    global current_input_lang, current_output_lang, language_change_flag
    if language_change_flag:
        current_input_lang = language_codes.get(input_lang.get(), "auto")
        current_output_lang = language_codes.get(output_lang.get(), "en")
        language_change_flag = False

def update_translation():
    global keep_running, language_change_flag

    while keep_running:
        # Check if language change is required and update settings if needed
        update_language_settings()

        r = sr.Recognizer()

        with sr.Microphone() as source:
            print("Speak Now!\n")
            audio = r.listen(source)

            try:
                speech_text = r.recognize_google(audio)
                # Transliterate text if needed
                speech_text_transliteration = transliterate_text(speech_text, lang_code=current_input_lang) if current_input_lang not in ('auto', 'en') else speech_text
                input_text.insert(tk.END, f"{speech_text_transliteration}\n")
                if speech_text.lower() in {'exit', 'stop'}:
                    keep_running = False
                    return
                
                translated_text = GoogleTranslator(source=current_input_lang, target=current_output_lang).translate(text=speech_text_transliteration)
                # print(translated_text)

                voice = gTTS(translated_text, lang=current_output_lang)
                voice.save('voice.mp3')
                playsound('voice.mp3')
                os.remove('voice.mp3')

                output_text.insert(tk.END, translated_text + "\n")
                
            except sr.UnknownValueError:
                output_text.insert(tk.END, "Could not understand!\n")
            except sr.RequestError:
                output_text.insert(tk.END, "Could not request from Google!\n")

        win.after(100, update_translation)

def run_translator():
    global keep_running, language_change_flag
    
    if not keep_running:
        keep_running = True
        language_change_flag = True  # Set language change flag before starting
        update_translation_thread = threading.Thread(target=update_translation)  # Use threading for translation
        update_translation_thread.daemon = True  # Set the thread as a daemon thread
        update_translation_thread.start()
        run_button.config(text="Stop Translation", command=stop_translator)  # Change button text to "Stop Translation"
    else:
        stop_translator()  # Stop translation if running

def stop_translator():
    global keep_running
    keep_running = False
    run_button.config(text="Start Translation", command=run_translator)  # Revert button text to "Start Translation"

def kill_execution():
    global keep_running
    keep_running = False

def open_about_page():  # about page
    about_window = tk.Toplevel()
    about_window.title("About")
    about_window.iconphoto(False, icon)

    # Create a link to the GitHub repository
    github_link = ttk.Label(about_window, text="github.com/SamirPaulb/real-time-voice-translator", underline=True, foreground="blue", cursor="hand2")
    github_link.bind("<Button-1>", lambda e: open_webpage("https://github.com/SamirPaulb/real-time-voice-translator"))
    github_link.pack()

    # Create a text widget to display the about text
    about_text = tk.Text(about_window, height=10, width=50)
    about_text.insert("1.0", """
    A machine learning project that translates voice from one language to another in real time while preserving the tone and emotion of the speaker, and outputs the result in MP3 format. Choose input and output languages from the dropdown menu and start the translation!
    """)
    about_text.pack()

    # Create a "Close" button
    close_button = tk.Button(about_window, text="Close", command=about_window.destroy)
    close_button.pack()

def open_webpage(url):  # Opens a web page in the user's default web browser.
    import webbrowser
    webbrowser.open(url)


# Update current languages when dropdown values change
def handle_language_change():
    global language_change_flag
    language_change_flag = True

# Create the "Run" button
run_button = tk.Button(win, text="Start Translation", command=run_translator)
run_button.place(relx=0.25, rely=0.9, anchor="c")

# Create the "Kill" button
kill_button = tk.Button(win, text="Kill Execution", command=kill_execution)
kill_button.place(relx=0.5, rely=0.9, anchor="c")

# Open about page button
#about_button = tk.Button(win, text="About this project", command=open_about_page)
#about_button.place(relx=0.75, rely=0.9, anchor="c")

# Bind language change
input_lang.bind("<<ComboboxSelected>>", lambda e: handle_language_change())
output_lang.bind("<<ComboboxSelected>>", lambda e: handle_language_change())

# Run the Tkinter event loop
win.mainloop()
