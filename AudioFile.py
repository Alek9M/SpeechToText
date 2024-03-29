import math
import os
from pydub import AudioSegment
import shutil


class AudioFile:

    def __init__(self, path: str):
        self._converted_audio = None
        self._converted_audio_path = None
        self.audio_pieces = []
        self.audio_pieces_paths = []
        if os.path.isfile(path):
            self._path = path
            if not self.is_file_name_same_as_folder():
                self.move_file_to_folder()
            self.convert_to_mp3()
            if not self.is_file_under_25mb():
                self.split_audio()
            else:
                self.audio_pieces = [self._converted_audio]
                self.audio_pieces_paths = [self._converted_audio_path]
            # self._file = open(path, "rb")

    def is_file_under_25mb(self):
        if os.path.isfile(self._converted_audio_path):
            # Get the size of the file in bytes
            file_size = os.path.getsize(self._converted_audio_path)

            # Convert bytes to megabytes (1 MB = 1024 * 1024 bytes)
            file_size_mb = file_size / (1024 * 1024)

            # Check if the file size is under 25 MB
            return file_size_mb < 25
        return False

    def _calculate_file_pieces(self):
        if os.path.isfile(self._converted_audio_path):
            # Get the size of the file in bytes
            file_size_bytes = os.path.getsize(self._converted_audio_path)

            # Convert max_size_mb to bytes
            max_size_bytes = 23 * 1024 * 1024

            return math.ceil(file_size_bytes / max_size_bytes)
        return 0

    def split_audio(self):
        num_pieces = self._calculate_file_pieces()
        # Calculate the duration of each piece
        piece_duration = math.ceil(self._converted_audio.duration_seconds / num_pieces) * 1000
        # Calculate the overlap in milliseconds
        overlap = min(3 * 1000, piece_duration)
        file_path, file_extension = os.path.splitext(self._converted_audio_path)

        for i in range(num_pieces):
            piece_path = f"{file_path}_{i}{file_extension}"
            if not os.path.exists(piece_path):
                # Calculate the start and end points for each piece with overlap
                start_point = max(0, i * piece_duration - overlap)
                end_point = min(self._converted_audio.duration_seconds * 1000, (i + 1) * piece_duration + overlap)

                # Extract the audio piece with overlap
                audio_piece = AudioFile.get_audio_piece(self._converted_audio, start_point, end_point)

                audio_piece.export(piece_path, format="mp3")

                # Append the audio piece to the list
                self.audio_pieces.append(audio_piece)
            self.audio_pieces_paths.append(piece_path)

    @staticmethod
    def get_audio_piece(audio, start_point, end_point):
        return audio[start_point:end_point]

    @staticmethod
    def convert_hh_mm_ss_to_audio_point(input_time):
        hours, minutes, seconds = input_time.split(':')
        return ((int(hours) * 3600) + (int(minutes) * 60) + int(seconds)) * 1000

    def is_file_name_same_as_folder(self):
        # Extract the filename and directory name
        filename = os.path.splitext(os.path.basename(self._path))[0]
        directory_name = os.path.basename(os.path.dirname(self._path))

        # Compare the filename with the directory name
        return filename == directory_name

    def move_file_to_folder(self):
        # Get the directory and filename from the file path
        directory, filename = os.path.split(self._path)

        # Create a folder with the name of the file (without extension)
        folder_name = os.path.splitext(filename)[0]
        folder_path = os.path.join(directory, folder_name)

        # Create the folder if it doesn't exist
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # Move the file into the created folder
        new_file_path = os.path.join(folder_path, filename)
        shutil.move(self._path, new_file_path)
        self._path = new_file_path

        return new_file_path

    @staticmethod
    def audio_from_mp3(file_path):
        if AudioFile.is_mp3(file_path):
            return AudioSegment.from_mp3(file_path)

    @staticmethod
    def is_mp3(file_path):
        file_path, file_extension = os.path.splitext(file_path)
        if file_extension == ".mp3": return True
        else: return False

    def convert_to_mp3(self):
        if os.path.isfile(self._path):
            # Extract the file extension
            file_path, file_extension = os.path.splitext(self._path)
            if file_extension == ".ogg":
                self._converted_audio_path = file_path + ".mp3"
                if not os.path.exists(self._converted_audio_path):
                    song = AudioSegment.from_ogg(self._path)
                    song.export(self._converted_audio_path, format="mp3")
                print( f"opening {self._converted_audio_path}")
                self._converted_audio = AudioFile.audio_from_mp3(self._converted_audio_path)
            elif file_extension == ".mp3":
                self._converted_audio = AudioFile.audio_from_mp3(self._path)
                self._converted_audio_path = self._path
            else:
                raise IOError(f'File extension {file_extension} not supported')
