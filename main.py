# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

import openai
import os
import PySimpleGUI as sg
from file_helpers import *
from prompts import *
import threading
import time
import whisper
print(whisper.__file__)
import timeit
from pydub import AudioSegment
from AudioFile import AudioFile
from TextProcessor import TextProcessor

def convert(filename: str, from_format: str, to_format: str) -> str:
    raw_audio = AudioSegment.from_file(f"{filename}.{from_format}", format=from_format)
    raw_audio.export(f"{filename}.{to_format}", format=to_format)
    return f"{filename}.{to_format}"



text_processor = TextProcessor()
openai.api_key = ""
client = openai #openai(api_key="")
aud = None


def process_file(file_path):
    print(f"Processing file {file_path}")
    # model = whisper.load_model("base")
    # result = model.transcribe(file_path, language='ru')
    # print(result["text"])
    # return
    aud = AudioFile(file_path)

    # Create a new window with the progress bar
    # progress_layout = [
    #     [sg.Text(f"Selected file: {file_path}")],
    #     [sg.ProgressBar(100, orientation="h", size=(20, 20), key="progressbar")],
    # ]
    # progress_window = sg.Window("Processing", progress_layout)
    # progress_bar = progress_window["progressbar"]

    # Create a new thread for the progress indicator loop
    # thread = threading.Thread(target=process_file, args=(file_path, progress_bar))
    # thread.start()

    # progress_window.read()  # Keep the window open until the thread completes

    # if not is_file_under_25mb(file_path):
    #     print(f"The file {file_path} is over 25 MB.")
    #     progress_window.close()
    #     exit(1)

    for path in aud.audio_pieces_paths:
        text_processor.add_path(text_file_path_for(path))
        if os.path.exists(text_file_path_for(path)):
            continue
        with open(path, "rb") as audio_file:
            print(f"transcribing {audio_file}")
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                prompt=conference_whisper_prompt
            )

        write_text_to_file_in_same_folder(path, transcript.text)

    process_text(aud)

    # progress_window.close()


def process_text(aud, text):
    i = -1
    for text in text_processor.split_into_under(7):
        tokens = len(TextProcessor.tokenize(text))
        if tokens == 0:
            break
        i += 1
        print(f"Tokens: {tokens}")
        if os.path.exists(text_file_path(aud._converted_audio_path, i)):
            continue

        with open(pretext_file_path(aud._converted_audio_path, i), "w") as full:
            full.write(text)

        response = client.chat.completions.create(
            model="gpt-4",
            temperature=0.2,
            messages=[
                {"role": "system",
                 "content": monologue_gpt_prompt},
                {"role": "user",
                 "content": text}
            ]
        )

        with open(text_file_path(aud._converted_audio_path, i), "w") as full:
            if response.choices[0].finish_reason == 'stop':
                full.write(response.choices[0].message.content)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    # file_path = ""  # "/Users/m/Projects/Speech To Text/1.m4a"

    sg.theme('DarkAmber')  # Add a touch of color
    # All the stuff inside your window.
    layout = [[sg.InputText(key="file_path", size=(40, 1)), sg.FileBrowse()],
              [sg.Text('Text file name'), sg.InputText()],
              [sg.Button('Transcript'), sg.Button('Transcript locally')],
              [sg.Button('Process')],
              [sg.Text('From:'), sg.Input(size=(8, 1)), sg.Text('To:'), sg.Input(size=(8, 1)), [sg.Button('Cut')]]] #, sg.Button('Process')

    # Create the Window
    window = sg.Window('OpenAI Transcriptor', layout)
    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Cancel':  # if user closes window or clicks cancel
            break
        else:
            if event == 'Process':
                if os.path.isfile(values['file_path']):
                    process_text(None, )
            elif not AudioFile.is_mp3(values['file_path']):
                values['file_path'] = convert(filename_at_path(values['file_path']), "m4a", "mp3")
            if event == 'Transcript':
                if os.path.isfile(values['file_path']):
                    process_file(values['file_path'])
            elif event == 'Transcript locally':
                if os.path.isfile(values['file_path']) and AudioFile.is_mp3(values['file_path']):
                    modelName = "large"
                    startModel = timeit.default_timer()
                    model = whisper.load_model(modelName)
                    loadedModel = timeit.default_timer()
                    print("Loaded", modelName, "in", loadedModel - startModel)
                    startTranscript = timeit.default_timer()
                    result = model.transcribe(values['file_path'])
                    endTranscript = timeit.default_timer()
                    print("Transcribed by", modelName, "in", endTranscript - startTranscript)
                    file_path, file_extension = os.path.splitext(values['file_path'])
                    with open(file_path + " local by " + modelName + ".txt", "w") as local:
                        local.write(result["text"])

            elif event == 'Cut':
                if os.path.isfile(values['file_path']):
                    fr = AudioFile.convert_hh_mm_ss_to_audio_point(values[1])
                    to = AudioFile.convert_hh_mm_ss_to_audio_point(values[2])
                    audio = AudioFile.audio_from_mp3(values['file_path'])
                    cut = AudioFile.get_audio_piece(audio, fr, to)
                    file_path, file_extension = os.path.splitext(values['file_path'])
                    cut.export(file_path + " from " + values[1] + " to " + values[2] + file_extension, format='mp3')

    window.close()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
