import compressors.huffman as canonical
from functools import reduce
from compressors.utils import frequency_dictionary, reverse_dict, group_bits, _TextCompressor, CompressionStats
import re

def _build_huffword_code(seq):
    freqs = frequency_dictionary(seq)
    huff_tree = canonical.build_huff_tree(freqs)
    code_table= canonical.build_code_table(huff_tree)
    return code_table
    
def huffword_encode(text):
    # Words huff tree
    words = re.findall(r'\w+', text)
    words_code = _build_huffword_code(words)

    # Non words huff tree
    nonwords = re.findall(r'\W+', text)
    nonwords_code = _build_huffword_code(nonwords)

    encoded_string = ""

    # When text start with non-word append 0, otherwise append 1
    starts_with = 0
    if text.startswith(words[0]):
        starts_with += 1
    
    # Append starts with as the first char
    encoded_string += str(starts_with)

    # Encode intercalating words and nonwords
    w_index = 0
    nw_index = 0

    #When starts with non words
    if not starts_with:
        encoded_string += nonwords_code[nonwords[0]]
    
    while w_index < len(words) or nw_index < len(nonwords):
        if w_index < len(words):
            word = words[w_index]
            encoded_string += words_code[word]
            w_index += 1
        
        if nw_index < len(nonwords):
            nonword = nonwords[nw_index]
            encoded_string += nonwords_code[nonword]
            nw_index += 1
    
    return {'encoded' : encoded_string,
            'words_meta' : (words, words_code),
            'non_words_meta': (nonwords, nonwords_code)}


def huffword_decode(encoded_text, words_code, nonwords_code):
    decoded_string = ""
    buffer = ''

    #First bit indicates if phrase starts with word or nonword
    starts_with = int(encoded_text[0])
    encoded_text = encoded_text[1:]

    rev_words_code = reverse_dict(words_code)
    rev_nonwords_code = reverse_dict(nonwords_code)

    nonword_flag = False

    # Starts with non_word
    if not starts_with:
        nonword_flag = True
    
    for s in encoded_text:
        if (buffer in rev_nonwords_code and nonword_flag) \
            or (buffer in rev_words_code and not nonword_flag):
            decoded_string += rev_words_code[buffer] if not nonword_flag else rev_nonwords_code[buffer]
            buffer = s
            nonword_flag = not nonword_flag
        else:
            buffer += s
    
    # Check if last iteration is also a symbol
    if (buffer in rev_nonwords_code and nonword_flag) \
            or (buffer in rev_words_code and not nonword_flag):
        last_symbol = rev_words_code[buffer] if not nonword_flag else rev_nonwords_code[buffer]
        decoded_string += last_symbol or ""

    return decoded_string

class HuffwordStats(CompressionStats):
    def _count_codes_size(self, symbols, keys):
        bits_stream = reduce(lambda x, y : x + y, symbols, "")
        keys_size =  reduce(lambda x, y: x + len(y), keys, 0) # Each char key is one byte
        bytes_stream = group_bits(bits_stream)
        return len(bytes_stream) + keys_size

    def __init__(self, originaltext, compressedtext, wordtable, nonwordtable):
        # Count the 0's and 1's as bits, and the symbols as chars
        words_table_size = self._count_codes_size(wordtable.values(), wordtable.keys())
        non_words_table_size = self._count_codes_size(nonwordtable.values(),wordtable.keys()) 
        self.originaltextsize = len(originaltext)
        self.compressedtextsize = len(compressedtext) + words_table_size + non_words_table_size

class HuffwordCompressor(_TextCompressor):
    def __init__(self):
        super().__init__()
        self.nonwords_codetable = {}
        self.words_codetable = {}
        self.encodedtext = ""

    def encode(self, text, print_stats=False):
        super().encode(text=text)
        response_map = huffword_encode(self.originaltext)
        self.encodedtext = response_map['encoded']
        self.words_codetable = response_map['words_meta'][1]
        self.nonwords_codetable = response_map['non_words_meta'][1]
        bytesencoded = group_bits(self.encodedtext)
        self.stats = HuffwordStats(self.originaltext, bytesencoded, self.words_codetable, self.nonwords_codetable)

        if print_stats:
            print(str(self.stats))

    def decode(self, print_output=False):
        super().decode()
        if self.encodedtext \
            and (self.nonwords_codetable or self.words_codetable):
            decoded_text = huffword_decode(self.encodedtext, self.words_codetable, self.nonwords_codetable)
            if print_output:
                print(decoded_text)

            return decoded_text
        else:
            raise Exception("No text to decode")
