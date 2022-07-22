import compressors.lz77 as canonical
from compressors.utils import _TextCompressor, CompressionStats
import re

def wlz77_encode(text):
    regex = r'\w+|\W+'
    words_list = re.findall(regex,text)
    return canonical._lz77_encode(words_list)

def wlz77_decode(tokens):
    decoded_words = []

    for t in tokens:
        lookahead, size, word = t
        if canonical.token_is_null(t):
            decoded_words.append(word)
            continue
        startpos = len(decoded_words) - lookahead
        endpos = startpos + size
        for pos in range(startpos, endpos):
            decoded_words.append(decoded_words[pos])
        
        print(decoded_words)

    return ''.join(decoded_words)


class WLz77Stats(CompressionStats):
    def __init__(self, originaltext, compressedtext):
        super().__init__(originaltext, compressedtext)

class WLz77Compressor(_TextCompressor):
    def __init__(self):
        super().__init__()
        self.tokens = []
        self.compressedtext = []
    
    def encode(self, text, print_stats=False):
        self.originaltext = text
        self.tokens = wlz77_encode(text)
        self.compressedtext = canonical.tokens_to_bytes(self.tokens)
        self.stats = WLz77Stats(self.originaltext, self.compressedtext)
        if print_stats:
            print(self.stats)
    
    def decode(self):
        super().decode()
        if self.tokens:
            print(wlz77_decode(self.tokens))
        else:
            raise Exception("No token to decode.")



