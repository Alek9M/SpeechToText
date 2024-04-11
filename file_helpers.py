import os


def filename_at_path(path):
    directory, filename = os.path.split(path)
    return directory + "/" + os.path.splitext(filename)[0]


def file_breakdown(path):
    directory, full_filename = os.path.split(path)
    filename, extension = os.path.splitext(full_filename)
    return directory, filename, extension


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
