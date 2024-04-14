import ffmpeg
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

from pydub import AudioSegment

openai.api_key = os.environ.get('OPENAI_KEY')
client = openai  # openai(api_key="")
aud = None


def process_audio(file_path, choice, locally=False):
    text_processor = TextProcessor()
    audio = AICompatableAudio(file_path)

    for path in audio.audio_pieces_paths:
        new_text_file_path = TextProcessor.text_file_path_for(path)
        text_processor.add_path(new_text_file_path)

        if not os.path.exists(new_text_file_path):
            print(f"transcribing {path}")
            transcript = ""
            if locally:
                model_name = "large"
                start_model = timeit.default_timer()
                model = whisper.load_model(model_name)  # the point
                loaded_model = timeit.default_timer()
                print("Loaded", model_name, "in", loaded_model - start_model)

                start_transcribing = timeit.default_timer()
                result = model.transcribe(path)  # the point
                end_transcribing = timeit.default_timer()
                print("Transcribed by", model_name, "in", end_transcribing - start_transcribing)

                transcript = result["text"]
                # file_path, file_extension = os.path.splitext(file_path)
                # with open(file_path + " local by " + model_name + ".txt", "w") as local:
                #     local.write(result["text"])
            else:
                with open(path, "rb") as audio_file:
                    start_transcribing = timeit.default_timer()
                    transcript = client.Audio.transcribe(model="whisper-1",
                        file=audio_file,
                        prompt=Buttons.whisper(choice))
                    end_transcribing = timeit.default_timer()
                    print("Transcribed by OpenAI in", end_transcribing - start_transcribing)
                    # transcript = client.Audio.transcriptions.create(
                    #     model="whisper-1",
                    #     file=audio_file,
                    #     prompt=Buttons.whisper(choice)
                    # )
                    transcript = transcript.text

            if len(transcript) > 0:
                TextProcessor.text_to_file_in_same_folder(path, transcript)

    # TODO: uncomment?
    # process_text(audio, text_processor, choice)

    # progress_window.close()


# def process_text(audio: AICompatableAudio, text_processor: TextProcessor, choice):
#     i = -1
#     for text in text_processor.split_into_under(7):
#         i += 1
#         process_raw(text, audio._converted_audio_path, choice, i)

def generate_post_for(text: str, n=1) -> str:
    response = client.ChatCompletion.create(
        model="gpt-4-turbo",
        temperature=1.15,
        max_tokens=1000 * n,
        n=n,
        messages=[
            {"role": "system",
             "content": instagram_post_prompt},
            {"role": "user",
             "content": text}
        ]
    )
    return response.choices

def create_posts(file_path, n):
    text = ""
    if n > 5 or n < 0:
        raise ValueError("n must be between 0 and 5")
    with open(file_path, "r") as orig:
        text = orig.read()
    if len(text) > 0:
        processor = TextProcessor()
        processor.add_path(file_path)
        choices = generate_post_for(processor.whole_text, n)
        for choice in choices:
            if choice.finish_reason == 'stop':
                directory, filename = os.path.split(file_path)
                post_path = os.path.join(directory, f"post {choices.index(choice)}.txt")
                with open(post_path, "w") as post:
                    post.write(choice.message.content)

def process_raw(text: str, origin_path: str, choice, model, context_window, i="") -> str:
    tokens = len(TextProcessor.tokenize(text))
    if tokens == 0:
        return
    print(f"Tokens: {tokens}")
    desired_file = text_file_path(origin_path, i)
    if os.path.exists(desired_file):
        raise ValueError("File already exists")

    with open(pretext_file_path(origin_path, i), "w") as full:
        full.write(text)

    response = client.ChatCompletion.create(
        model=model,
        temperature=0.2,
        messages=[
            {"role": "system",
             "content": Buttons.gpt(choice)},
            {"role": "user",
             "content": text}
        ]
    )
    finish_reason = response.choices[0].finish_reason
    if finish_reason == 'stop':
        with open(desired_file, "w") as full:
            full.write(response.choices[0].message.content)
            return response.choices[0].message.content
    elif finish_reason == "length":
        raise ValueError("Text too long")
    else:
        raise ValueError("Incorrect OpenAI finish reason")


# enum for buttons

def process(file_path, choice, model="gpt-4", context_window=7):
    print("Processing")
    text = ""
    processed_text = ""
    with open(file_path, "r") as orig:
        text = orig.read()
    if len(text) == 0:
        raise ValueError("File is empty")

    processor = TextProcessor()
    processor.add_path(file_path)
    i = -1
    for text_part in processor.split_into_under(context_window):
        i += 1
        processed_text += process_raw(text_part, file_path, choice, model, context_window, i) + "\n"
    directory, filename, extension = file_breakdown(file_path)
    with open(os.path.join(directory, f"{filename}_processed_whole.txt"), "w") as processed:
        processed.write(processed_text)



def cut(file_path, values):
    starting_point = AICompatableAudio.convert_hh_mm_ss_to_audio_point(values[0])
    finishing_point = AICompatableAudio.convert_hh_mm_ss_to_audio_point(values[1])

    # audio_input = ffmpeg.input(file_path)
    # audio_cut = audio_input.audio.filter('atrim', start=starting_point/1000, end=finishing_point/1000)
    # audio_output = ffmpeg.output(audio_cut, file_path + 'test.mp3')
    # ffmpeg.run(audio_output)

    audio = None
    if AICompatableAudio.is_mp3(file_path):
        audio = AICompatableAudio.audio_from_mp3(file_path)
    else:
        # audio = AudioSegment.from_file(AICompatableAudio(file_path)._converted_audio_path)
        audio = AICompatableAudio.audio_from_file(file_path)
        # raise ValueError("Only supports mp3 files")

    a_cut = AICompatableAudio.get_audio_piece(audio, starting_point, finishing_point)
    file_path, file_extension = os.path.splitext(file_path)
    # directory, filename, extension = file_breakdown(file_path)

    a_cut.export(file_path + " from " + values[0] + " to " + values[1] + ".mp3", format='mp3')


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
    TRANSCRIPT = "Transcribe online"
    LOCAL = "Transcribe locally"
    CUT = "Cut out a piece"
    POST = "Generate Instagram posts"
    LIST_PODCAST = "Podcast"
    LIST_CONFERENCE = "Conference"
    CHEAP = "Process text cheaply"

    @staticmethod
    def whisper(choice):
        if len(choice) != 1:
            raise ValueError("Specify type of audio")

        if choice[0] == Buttons.LIST_PODCAST.value:
            return podcast_prompt
        else:
            return conference_whisper_prompt

    @staticmethod
    def gpt(choice):
        if choice[0] == Buttons.LIST_PODCAST.value:
            return monologue_gpt_prompt
        else:
            return dialogue_gpt_prompt


FILE_PATH_KEY = "file_path"
TEXT_FILE_PATH_KEY = "file_path0"

def get_file_path_from(values, key=FILE_PATH_KEY) -> str:
    path = values[key]
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
                process(get_file_path_from(values, TEXT_FILE_PATH_KEY), values[2])
            elif event == Buttons.CHEAP.value:
                process(get_file_path_from(values, TEXT_FILE_PATH_KEY), values[2], "gpt-3.5-turbo", 14)
            elif event == Buttons.POST.value:
                create_posts(get_file_path_from(values, TEXT_FILE_PATH_KEY), int(values[3]))
            elif event == Buttons.TRANSCRIPT.value:
                process_audio(get_file_path_from(values), values[2])
            elif event == Buttons.LOCAL.value:
                # local_trans(get_file_path_from(values))
                process_audio(get_file_path_from(values), values[2], True)
            elif event == Buttons.CUT.value:
                cut(get_file_path_from(values), values)

        except ValueError as error:
            print(error)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    sg.theme('DarkPurple')
    layout = [
        [sg.Text('Audio file'), sg.InputText(key=FILE_PATH_KEY, size=(40, 1)), sg.FileBrowse()],
        [sg.Button(Buttons.TRANSCRIPT.value), sg.Button(Buttons.LOCAL.value)],
        [sg.Text('From:'), sg.Input(size=(8, 1)), sg.Text('To:'), sg.Input(size=(8, 1)), sg.Button(Buttons.CUT.value)],
        [sg.Text('Text file '), sg.InputText(key=TEXT_FILE_PATH_KEY, size=(40, 1)), sg.FileBrowse()],
        [sg.Button(Buttons.PROCESS.value), sg.Button(Buttons.CHEAP.value),
         sg.Listbox([Buttons.LIST_PODCAST.value, Buttons.LIST_CONFERENCE.value], size=(10, 2)),
         sg.Button(Buttons.POST.value), sg.Input(default_text='2', size=(1,1))],
    ]
    # , sg.Button('Process')

    window = sg.Window('OpenAI Transcriptor', layout)

    event_loop()

    window.close()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
