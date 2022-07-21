from typing import Tuple, NewType
from compressors.utils import _TextCompressor, CompressionStats


Token = NewType("TokenType", Tuple[int, int, str])

# To bytes to store token numbers
MAX_OFFSET = 2047 # Offset 11 bits
MAX_LENGTH = 31 # Length 5 bits

def _token_is_null(token):
    return not (token[0] or token[1])


def _find_first_match(dictionary, target):
    dict_size = len(dictionary)
    end = dict_size - 1
    start = dict_size - len(target)
    gobackpointer = 0

    while start >= 0:
        gobackpointer = dict_size - start
        if gobackpointer > MAX_OFFSET:
            break

        if dictionary[start:end+1] == target:
            return gobackpointer

        start -=1
        end -= 1

def _find_best_match_seq(dictionary, lookaheadbuffer):

    labpointer = 0
    gobackpointer = 0
    besttoken = Token((0, 0, lookaheadbuffer[0]))

    while labpointer < len(lookaheadbuffer) and labpointer < MAX_LENGTH:

        gobackpointer = _find_first_match(
            dictionary, lookaheadbuffer[:labpointer+1])

        if not gobackpointer:
            return besttoken

        labpointer += 1

        besttoken = Token((gobackpointer, labpointer, ""))

    return besttoken


def _lz77_encode(text):
    window = 0
    encoded_dict = []

    while window < len(text):
        token = _find_best_match_seq(
            dictionary=text[:window], lookaheadbuffer=text[window:])
        encoded_dict.append(token)
        if not _token_is_null(token):
            _, size, _ = token
            window += size
            continue

        window += 1

    return encoded_dict


def _lz77_decode(tokens):
    decodedtoken = ""
    for token in tokens:
        lookahead, size, char = token
        if _token_is_null(token):
            decodedtoken += char
            continue
        subtstrstart = len(decodedtoken) - lookahead
        substrend = subtstrstart + size
        decodedtoken += decodedtoken[subtstrstart:substrend]

    return decodedtoken


def _tokens_to_bytes(tokens):
    size_bits = 5
    
    b_arr = bytearray()

    for t in tokens:
        offset, size, char = t

        if _token_is_null(t):
            b_arr.append(0)
            b_arr += bytearray(char.encode())
            continue

        two_bytes_offset_size = (offset << size_bits) + size

        # append two last bytes
        mask = 0b11111111
        offset_byte = (two_bytes_offset_size >> 8) & mask
        size_byte = (two_bytes_offset_size) & mask
        b_arr.append(size_byte)
        b_arr.append(offset_byte)
    return b_arr

class Lz77Stats(CompressionStats):
    def __init__(self, originaltext, compressedtext):
        super().__init__(originaltext, compressedtext)


class Lz77Compressor(_TextCompressor):
    def __init__(self):
        super().__init__()
        self.tokens = []
        self.compressedtext = []

    def encode(self, text, print_stats=False):
        super().encode(text)
        self.tokens = _lz77_encode(self.originaltext)
        self.compressedtext = _tokens_to_bytes(self.tokens)
        self.stats = Lz77Stats(self.originaltext, self.compressedtext)
        if print_stats:
            print(str(self.stats))

    def decode(self):
        super().decode()
        if self.tokens:
            print(_lz77_decode(self.tokens))
        else:
            raise Exception("No token to decode.")
