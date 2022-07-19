import re
from compressors.utils import Node, _TextCompressor, CompressionStats, reverse_dict, frequency_dictionary
from functools import reduce
import heapq


def _build_huff_tree(text_freq):
    florest = []

    # Building florest
    for data, weigth in text_freq.items():
        root = Node(weigth, data)
        heapq.heappush(florest, root)

    while len(florest) > 1:
        t1 = heapq.heappop(florest)
        t2 = heapq.heappop(florest)

        root = Node(t1.weigth + t2.weigth)
        root.left = t1
        root.right = t2
        heapq.heappush(florest, root)

    return florest[0]


def _build_code_table(h_tree, path=""):
    if(not h_tree):
        return {}
    if(h_tree.is_leaf()):
        return {h_tree.data: path}
    return {**_build_code_table(h_tree.left, path + "0"), **_build_code_table(h_tree.right, path + "1")}


def _huffman_encode(text):
    freqs = frequency_dictionary(text)
    huff_tree = _build_huff_tree(freqs)
    code_table = _build_code_table(huff_tree)

    encoded_string = ""
    for char in text:
        encoded_string += code_table[char]

    return (encoded_string, code_table, huff_tree, freqs)


def _huffman_decode(encoded_text, code_table):
    buffer = ""
    decoded_text = ""
    inverse_code = reverse_dict(code_table)

    for s in encoded_text:
        symbol = inverse_code[buffer] if buffer in inverse_code else ""
        if(symbol):
            decoded_text = decoded_text + symbol
            buffer = s
        else:
            buffer = buffer + s

    # When buffer is increased on the last iteration
    if(buffer in inverse_code):
        last_symbol = inverse_code[buffer]
        decoded_text += last_symbol or ""

    return decoded_text

def _group_bits(bit_stream):
    return re.findall(r'\d{1,8}', bit_stream)

class HuffmanStats(CompressionStats):
    def _count_codes_size(self, symbols):
        bits_stream = reduce(lambda x, y : x + y, symbols, "")
        bytes_stream = _group_bits(bits_stream)
        return len(bytes_stream)

    def __init__(self, originaltext, compressedtext, codetable):
        table_size = self._count_codes_size(codetable.values()) + len(codetable) # Count the 0's and 1's as bits, and the symbols as chars
        self.originaltextsize = len(originaltext)
        self.compressedtextsize = len(compressedtext) + table_size

class HuffmanCompressor(_TextCompressor):
    def __init__(self, text):
        super().__init__(text)
        self.codetable = {}
        self.huff_tree = None
        self.prob_table = None
        self.encodedtext = ""

    def encode(self, print_stats=False):
        super().encode()
        encodedtext, table, tree, freqs = _huffman_encode(self.originaltext)
        self.encodedtext = encodedtext
        self.codetable = table
        self.huff_tree = tree
        self.prob_table = freqs
        bytesencoded = _group_bits(self.encodedtext)
        self.stats = HuffmanStats(self.originaltext, bytesencoded, self.codetable)

        if print_stats:
            print(str(self.stats))

    def decode(self, print_output=False):
        super().decode()
        if self.encodedtext and self.codetable:
            decoded_text = _huffman_decode(self.encodedtext, self.codetable)
            if print_output:
                print(decoded_text)

            return decoded_text
        else:
            raise Exception("No text to decode")
