from typing import Tuple, NewType
from utils import _TextCompressor, CompressionStats


Token = NewType("TokenType", Tuple[int, int, str])

def _token_is_null(token):
    return not (token[0] or token[1])

def _find_first_match(dictionary, target):
    start = 0
    end = len(target) - 1

    while end < len(dictionary):
        if dictionary[start:end+1] == target:
            return start
        start += 1
        end += 1
    

def _find_best_match_seq(dictionary, lookaheadbuffer):
    
    labpointer = 0
    besttoken = Token((0, 0, lookaheadbuffer[0]))

    while labpointer < len(lookaheadbuffer):
        matchpointer = _find_first_match(dictionary, lookaheadbuffer[:labpointer+1])

        if not matchpointer:
            return besttoken
        
        labpointer += 1
        gobackpointer = len(dictionary) - matchpointer
        besttoken = Token((gobackpointer, labpointer, ""))
    
    return besttoken


def _lz77_encode(text):
    window = 0
    encoded_dict = []

    while window < len(text):
        token = _find_best_match_seq(dictionary=text[:window], lookaheadbuffer=text[window:])
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
    b_arr = bytearray()
    for t in tokens:
        newbytes = bytearray(0) + bytearray(t[2].encode()) if _token_is_null(t) else bytearray(t[0:2])
        b_arr += newbytes
    return b_arr

class Lz77Stats(CompressionStats):
    def __init__(self, originaltext, compressedtext):
        super().__init__(originaltext, compressedtext)

class Lz77Compressor(_TextCompressor):
    def __init__(self, text):
        super().__init__(text)
        self.tokens = []
        self.compressedtext = []
    
    def encode(self):
        super().encode()
        self.tokens = _lz77_encode(self.originaltext)
        self.compressedtext = _tokens_to_bytes(self.tokens)
        self.stats = Lz77Stats(self.originaltext, self.compressedtext)
        print(str(self.stats))
    
    def decode(self):
        super().decode()
        if self.tokens:
            print(_lz77_decode(self.tokens))
        else:
            raise Exception("No token to decode.")

        

