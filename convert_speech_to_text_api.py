import openai
import tkinter as tk
from tkinter import filedialog
from pydub import AudioSegment
from pathlib import Path
import os
import json
import pyperclip

"""
Authors: Lawson Fuller and OpenAI ChatGPT (Most of the coding was done by OpenAI ChatGPT)
Purpose: Easy GUI for Using OpenAI Whisper
March 2, 2023
"""

openai.api_key = "" #TODO: You must put your OpenAI API key here in order to successfully run the code!

def convert_speech_to_text(mp3_file_path, mode):
    """
    Here, we will be using openai to make the API call to convert speech to text, tkinter for creating the GUI, and tkfilebrowser for selecting files.
    :param mp3_file_path: str
    :param mode: str
    :return: string of transcript in form "{ \n text: *your_text_string* \n }".
    """
    # Here, we are using the whisper model to convert the speech to text. You can tweak the parameters to adjust the accuracy of the conversion.
    # Note: you need to be using OpenAI Python v0.27.0 for the code below to work
    audio_file = open(mp3_file_path, "rb")
    if mode=="transcribe":
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
    if mode=="translate":
        transcript = openai.Audio.translate("whisper-1", audio_file)
    return str(transcript)

def select_file():
    """convert speech to text using OpenAI's whisper API
    """
    # This function opens a file dialog box to let your mom select the audio file. If a file is selected, it displays the file path in the GUI.
    file_path = filedialog.askopenfilename()
    if file_path:
        text_input.delete("1.0", tk.END)
        text_input.insert(tk.END, file_path)
        # Set the initial directory of the save_location dialog box to the directory of the selected audio file
        save_location = os.path.dirname(file_path)
        if save_location:
            save_input.delete("1.0", tk.END)
            save_input.insert(tk.END, save_location)
            check_and_enable_conversion_button()

def select_save_location():
    """
    handle the file selection
    """
    # opens a directory dialog box to let your mom select the save location. If a location is selected, it displays the location in the GUI.
    save_location = filedialog.askdirectory()
    if save_location:
        save_input.delete("1.0", tk.END)
        save_input.insert(tk.END, save_location)

        check_and_enable_conversion_button()

def file_size_is_small_enough(file_path):
    """
    OpenAI's Whisper doesn't allow audio greater than 25 MB. So we'll restrict that here.
    """
    # get the size of the file in bytes
    file_size = os.path.getsize(file_path)

    # convert to megabytes
    file_size_mb = file_size / (1024 * 1024)

    # check if the file size is less than or equal to 25 MB
    if file_size_mb <= 25:
        print(f"File is {file_size_mb} MB.")
        return True
    else:
        print("File is too large! Abandoning process.")
        return False

def check_and_enable_conversion_button():
    # Enable/disable the convert button based on whether both the audio file and save location have been selected
    audio_file = text_input.get("1.0", tk.END).strip()
    if audio_file:
        convert_button.config(state="normal")
    else:
        convert_button.config(state="disabled")

def convert_to_mp3(file_path):
    input_file = Path(file_path)
    output_file = input_file.with_suffix('.mp3')

    # Check if the input file is already an MP3 file
    if input_file.suffix == '.mp3':
        print(f"{file_path} is already an MP3 file. Skipping conversion...")
        return file_path

    # Convert to MP3 if the input file is not an MP3 file
    print(f"Converting {file_path} to MP3...")
    audio = AudioSegment.from_file(file_path, format=input_file.suffix[1:])
    audio.export(output_file, format='mp3')
    print(f"Conversion complete. MP3 file saved to {output_file}")
    return str(output_file)


def convert():
    """function to handle the conversion"""
    mode = mode_var.get()

    # This function reads the audio file and converts it to bytes. It then calls the convert_speech_to_text function to convert the speech to text. Finally, it writes the text to a file in the selected save location.
    audio_file = text_input.get("1.0", tk.END).strip()
    save_location = save_input.get("1.0", tk.END).strip()
    # Convert to mp3 if file is not already in mp3 format
    mp3_file_path = convert_to_mp3(audio_file)
    if mp3_file_path and save_location and file_size_is_small_enough(mp3_file_path):
        text = convert_speech_to_text(mp3_file_path, mode)
        filename = os.path.splitext(os.path.basename(mp3_file_path))[0]
        with open(f"{save_location}/{filename}.txt", "w", encoding='utf-8') as f:
            extracted_text = json.loads(text)['text']
            f.write(extracted_text)
            pyperclip.copy(extracted_text)
            print("Copied to clipboard: "+extracted_text+"\n-------------\n")

# Here, we create the GUI using the tkinter library.
# We create a window with the title "Speech to Text Converter" and set its size to 800x600 pixels.
# We then create a label for the audio file selection, a text input field for displaying the file path,
# and a button to open the file dialog box.
# Similarly, we create a label, a text input field, and a button for the save location selection.
# Finally, we create a button to trigger the conversion and pack all the widgets to display them on the window.

root = tk.Tk()
root.title("Speech to Text Converter: Powered by OpenAI Whisper")
root.geometry("800x600")

### This code creates a StringVar variable mode_var that stores the selected mode (defaulting to "transcribe").
# It then creates a label and two Radiobutton widgets that allow the user to toggle between the two modes.
# The variable option of the Radiobutton widgets is set to mode_var, so that the selected mode is automatically
# stored in mode_var. Finally, the value option of each Radiobutton widget is set to the corresponding mode
# ("transcribe" or "translate").

font_type = "Arial"
font_size = 24

# create a variable to store the selected mode
mode_var = tk.StringVar(value="transcribe")

# create a label and Radiobuttons to select the mode
mode_label = tk.Label(root, text="Select mode:", font=(font_type, font_size, "bold"))
mode_label.pack()
transcribe_button = tk.Radiobutton(root, text="Transcribe", variable=mode_var, value="transcribe", font=(font_type, font_size), indicatoron=0, selectcolor="green")
translate_button = tk.Radiobutton(root, text="Translate", variable=mode_var, value="translate", font=(font_type, font_size), indicatoron=0, selectcolor="green")
transcribe_button.pack()
translate_button.pack()

# Select audio file label
text_label = tk.Label(root, text="Select audio file:", font=(font_type, font_size, "bold"))
text_label.pack(pady=10)

# Text input box to display selected audio file
text_input = tk.Text(root, height=1, font=(font_type, round(font_size*2.0/3)))
text_input.pack(pady=5)

# Button to browse and select audio file
text_button = tk.Button(root, text="Browse", command=select_file, font=(font_type, font_size))
text_button.pack(pady=5)

# Select save location label
save_label = tk.Label(root, text="Select save location:", font=(font_type, font_size, "bold"))
save_label.pack(pady=10)

# Text input box to display selected save location
save_input = tk.Text(root, height=1, font=(font_type, round(font_size*2.0/3)))
save_input.pack(pady=5)

# Button to browse and select save location
save_button = tk.Button(root, text="Browse", command=select_save_location, font=(font_type, font_size))
save_button.pack(pady=5)

convert_button = tk.Button(root, text="Convert", command=convert, font=(font_type, font_size, "bold"))
convert_button.config(state='disabled')
convert_button.pack(pady=10)

root.mainloop()