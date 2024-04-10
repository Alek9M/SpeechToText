import openai
import PySimpleGUI as sg
from file_helpers import *
from prompts import *
import whisper
import timeit
from AICompatableAudio import AICompatableAudio
from TextProcessor import TextProcessor
from enum import Enum
from dotenv import load_dotenv

openai.api_key = os.environ.get('OPENAI_KEY')
client = openai  # openai(api_key="")
aud = None


def process_audio(file_path, locally=False):
    text_processor = TextProcessor()
    audio = AICompatableAudio(file_path)

    for path in audio.audio_pieces_paths:
        new_text_file_path = TextProcessor.text_file_path_for(path)
        text_processor.add_path(new_text_file_path)

        if not os.path.exists(new_text_file_path):
            with open(path, "rb") as audio_file:
                print(f"transcribing {audio_file}")
                transcript = ""
                if locally:
                    model_name = "large"
                    start_model = timeit.default_timer()
                    model = whisper.load_model(model_name)  # the point
                    loaded_model = timeit.default_timer()
                    print("Loaded", model_name, "in", loaded_model - start_model)

                    start_transcribing = timeit.default_timer()
                    result = model.transcribe(file_path)  # the point
                    end_transcribing = timeit.default_timer()
                    print("Transcribed by", model_name, "in", end_transcribing - start_transcribing)

                    transcript = result["text"]
                    # file_path, file_extension = os.path.splitext(file_path)
                    # with open(file_path + " local by " + model_name + ".txt", "w") as local:
                    #     local.write(result["text"])
                else:
                    transcript = client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        prompt=conference_whisper_prompt
                    )
                    transcript = transcript.text

            if len(transcript) > 0:
                TextProcessor.text_to_file_in_same_folder(path, transcript)

    process_text(audio, text_processor)

    # progress_window.close()


def process_text(audio: AICompatableAudio, text_processor: TextProcessor):
    i = -1
    for text in text_processor.split_into_under(7):
        tokens = len(TextProcessor.tokenize(text))
        if tokens == 0:
            break
        i += 1
        print(f"Tokens: {tokens}")
        if os.path.exists(text_file_path(audio._converted_audio_path, i)):
            continue

        with open(pretext_file_path(audio._converted_audio_path, i), "w") as full:
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

        with open(text_file_path(audio._converted_audio_path, i), "w") as full:
            if response.choices[0].finish_reason == 'stop':
                full.write(response.choices[0].message.content)


# enum for buttons

def process(file_path):
    print("Processing")
    process_text()


def cut(file_path, values):
    starting_point = AICompatableAudio.convert_hh_mm_ss_to_audio_point(values[1])
    finishing_point = AICompatableAudio.convert_hh_mm_ss_to_audio_point(values[2])
    audio = None
    if AICompatableAudio.is_mp3(file_path):
        audio = AICompatableAudio.audio_from_mp3(file_path)
    else:
        audio = AICompatableAudio.audio_from_file(file_path)
        # raise ValueError("Only supports mp3 files")

    a_cut = AICompatableAudio.get_audio_piece(audio, starting_point, finishing_point)
    file_path, file_extension = os.path.splitext(file_path)
    a_cut.export(file_path + " from " + values[1] + " to " + values[2] + file_extension, format='mp3')


# def local_trans(file_path):
#     if AICompatableAudio.is_mp3(file_path):
#         modelName = "large"
#         startModel = timeit.default_timer()
#         model = whisper.load_model(modelName)
#         loadedModel = timeit.default_timer()
#         print("Loaded", modelName, "in", loadedModel - startModel)
#         startTranscript = timeit.default_timer()
#         result = model.transcribe(file_path)
#         endTranscript = timeit.default_timer()
#         print("Transcribed by", modelName, "in", endTranscript - startTranscript)
#         file_path, file_extension = os.path.splitext(file_path)
#         with open(file_path + " local by " + modelName + ".txt", "w") as local:
#             local.write(result["text"])


class Buttons(Enum):
    PROCESS = "Process text"
    TRANSCRIPT = "Transcript online"
    LOCAL = "Transcript locally"
    CUT = "Cut out a piece"


FILE_PATH_KEY = "file_path"
TEXT_FILE_PATH_KEY = "file_path"


def get_file_path_from(values) -> str:
    path = values[FILE_PATH_KEY]
    if os.path.isfile(path):
        return path
    else:
        raise ValueError("File is unavailable")


def event_loop():
    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        try:
            event, values = window.read()

            if event == sg.WIN_CLOSED or event == 'Cancel':  # if user closes window or clicks cancel
                break

            if event == Buttons.PROCESS.value:
                process(get_file_path_from(values))
            elif event == Buttons.TRANSCRIPT.value:
                process_audio(get_file_path_from(values))
            elif event == Buttons.LOCAL.value:
                # local_trans(get_file_path_from(values))
                process_audio(get_file_path_from(values), True)
            elif event == Buttons.CUT.value:
                cut(get_file_path_from(values), values)

        except ValueError as error:
            print(error)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    sg.theme('DarkAmber')
    layout = [
        [sg.Text('Audio file'), sg.InputText(key=FILE_PATH_KEY, size=(40, 1)), sg.FileBrowse()],
        [sg.Button(Buttons.TRANSCRIPT.value), sg.Button(Buttons.LOCAL.value)],
        [sg.Text('From:'), sg.Input(size=(8, 1)), sg.Text('To:'), sg.Input(size=(8, 1)), sg.Button(Buttons.CUT.value)],
        [sg.Text('Text file '), sg.InputText(key=TEXT_FILE_PATH_KEY, size=(40, 1)), sg.FileBrowse()],
        [sg.Button(Buttons.PROCESS.value)],
    ]
    # , sg.Button('Process')

    window = sg.Window('OpenAI Transcriptor', layout)

    event_loop()

    window.close()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
