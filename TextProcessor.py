import math
import tiktoken


class TextProcessor:
    def __init__(self):
        self._texts_paths = list()

    def add_path(self, path):
        if path not in self._texts_paths:
            self._texts_paths.append(path)

    @property
    def total_tokens(self):
        return len(TextProcessor.tokenize(self.whole_text))

    @staticmethod
    def tokenize(text):
        encoding = tiktoken.encoding_for_model('gpt-4')#('gpt-4')  # ('gpt-3.5-turbo')
        return encoding.encode(text)

    @property
    def whole_text(self):
        whole_text = ''
        self._texts_paths.sort()
        for path in self._texts_paths:
            with open(path, 'r') as part:
                part = part.read()
                whole_text = whole_text + part

        return whole_text

    @staticmethod
    def find_next_sentence_index(input_string, current_index):
        sentence_endings = set('.!?')

        # Find the next occurrence of '.', '!', or '?' after the current index
        next_index = min((input_string.find(char, current_index) for char in sentence_endings if char in input_string),
                         default=-1)

        # Find the last index of the string
        last_index = len(input_string) - 1

        # Return the minimum of the next index and the last index
        return min(next_index + 1, last_index)

    def split_into_under(self, limit):
        piece_limit = (limit / 2) * 1000
        num_pieces = math.ceil(self.total_tokens / piece_limit)
        whole = self.whole_text
        piece_duration = round(len(whole) / num_pieces)
        parts = list()
        last_end = -1
        for i in range(num_pieces):
            start_point = max(last_end, i * piece_duration)
            end_point = TextProcessor.find_next_sentence_index(whole, min(len(whole) - 1, (i + 1) * piece_duration))
            parts.append(whole[start_point:end_point])
            last_end = end_point

        return parts
