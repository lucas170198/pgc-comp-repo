from collections import deque
from typing import Tuple, NewType
from compressors.utils import _TextCompressor, CompressionStats

Token = NewType("TokenType", Tuple[int, int, str])

# To bytes to store token numbers
MAX_OFFSET = 2047 # Offset 11 bits
MAX_LENGTH = 30 # Length 5 bits'

def token_is_null(token):
    return not (token[0] or token[1])

def _substring_match_size(dict,target):
    pointer = 0
    while pointer < len(target) and pointer < len(dict) and pointer <= MAX_LENGTH:
        if dict[pointer] == target[pointer]:
            pointer += 1
            continue
        break
    return pointer

def _find_best_match_seq(dictionary, lookaheadbuffer, memoized_chars):
    start_symbol = lookaheadbuffer[0]
    dict_size = len(dictionary)
    best_token = Token((0, 0, lookaheadbuffer[0]))

    if (start_symbol not in memoized_chars) or not dictionary:
        return best_token
    
    # removing invalid symbols
    starts = list(memoized_chars[start_symbol])
    for s in starts:
        if dict_size - s > MAX_OFFSET:
            memoized_chars[start_symbol].popleft()
    
    for start in memoized_chars[start_symbol]:
        if best_token[1] == MAX_LENGTH:
            break
        size = _substring_match_size(dictionary[start:], lookaheadbuffer)
        if size > best_token[1]:
            goback = dict_size - start
            best_token = Token((goback, size, ""))
    
    return best_token

def _insert_symbols(symbol_dict, new_symbols, old_window_size):
    for i, symbol in enumerate(new_symbols):
        if symbol not in symbol_dict:
            symbol_dict[symbol] = deque()

        symbol_dict[symbol].append(i + old_window_size - 1)

def _lz77_encode(text):
    window = 0
    encoded_dict = []
    memoized_chars = {}
    table_size = 0

    while window < len(text):
        token = _find_best_match_seq(
            dictionary=text[:window], lookaheadbuffer=text[window:], memoized_chars=memoized_chars)
        encoded_dict.append(token)
        if not token_is_null(token):
            _, size, _ = token
            new_symbols_start = window
            window += size
            _insert_symbols(memoized_chars, text[new_symbols_start : window], new_symbols_start + 1)
            table_size += size
            continue
        
        # Inserting one symbol
        new_symbol = text[window]
        if new_symbol not in memoized_chars:
            memoized_chars[new_symbol] = deque()

        memoized_chars[new_symbol].append(window)
        table_size += 1
        window += 1

    return encoded_dict


def _lz77_decode(tokens):
    decodedtoken = ""
    for token in tokens:
        lookahead, size, char = token
        if token_is_null(token):
            decodedtoken += char
            continue
        subtstrstart = len(decodedtoken) - lookahead
        substrend = subtstrstart + size
        decodedtoken += decodedtoken[subtstrstart:substrend]

    return decodedtoken


def tokens_to_bytes(tokens):
    size_bits = 5
    
    b_arr = bytearray()

    for t in tokens:
        offset, size, s = t

        if token_is_null(t):
            b_arr.append(0)
            b_arr += bytearray(s.encode())
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
        self.compressedtext = tokens_to_bytes(self.tokens)
        self.stats = Lz77Stats(self.originaltext, self.compressedtext)
        if print_stats:
            print(str(self.stats))

    def decode(self):
        super().decode()
        if self.tokens:
            print(_lz77_decode(self.tokens))
        else:
            raise Exception("No token to decode.")