# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

from openai import OpenAI
import os


def write_text_to_file_in_same_folder(file_path, text):
    # Extract the directory and filename from the provided file path
    directory, filename = os.path.split(file_path)

    # Create the new file path with the same filename but in the same directory
    new_file_path = os.path.join(directory, f"{os.path.splitext(filename)[0]}.txt")

    # Write the text to the new file
    with open(new_file_path, 'w') as file:
        file.write(text)

    print(f"Text written to {new_file_path}")


def is_file_under_25mb(file_path):
    # Get the size of the file in bytes
    file_size = os.path.getsize(file_path)

    # Convert bytes to megabytes (1 MB = 1024 * 1024 bytes)
    file_size_mb = file_size / (1024 * 1024)

    # Check if the file size is under 25 MB
    return file_size_mb < 25


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    file_path = "/Users/m/Projects/Speech To Text/1.m4a"
    if not is_file_under_25mb(file_path):
        print(f"The file {file_path} is over 25 MB.")
        exit(1)
    client = OpenAI(api_key="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")

    audio_file = open(file_path, "rb")
    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file
    )

    print(transcript)
    write_text_to_file_in_same_folder(file_path, transcript.text)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
