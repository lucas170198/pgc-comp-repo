import compressors.huffman as canonical
from compressors.utils import frequency_dictionary, reverse_dict
import re

#TODO: Convertion to bytes

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
