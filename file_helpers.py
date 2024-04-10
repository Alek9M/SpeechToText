import os


def filename_at_path(path):
    directory, filename = os.path.split(path)
    return directory + "/" + os.path.splitext(filename)[0]

def text_file_path(path, i):
    # Extract the directory and filename from the provided file path
    directory, filename = os.path.split(path)

    # Create the new file path with the same filename but in the same directory
    return os.path.join(directory, f"{os.path.splitext(filename)[0]}_processed_{i}.txt")


def pretext_file_path(path, i):
    # Extract the directory and filename from the provided file path
    directory, filename = os.path.split(path)

    # Create the new file path with the same filename but in the same directory
    return os.path.join(directory, f"{os.path.splitext(filename)[0]}_preprocessed_{i}.txt")

