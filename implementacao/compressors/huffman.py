from mimetypes import init
from utils import Node, PriorityQueue, _TextCompressor, CompressionStats, reverse_dict


def _frequency_dictionary(text):
    freqs = {}
    for character in text:
        if character in freqs:
            freqs[character] += 1
        else:
            freqs[character] = 1
    return freqs


def _build_huff_tree(text_freq):
    florest = PriorityQueue()

    # Building florest
    for data, weigth in text_freq.items():
        root = Node(weigth, data)
        florest.queue_add(root)

    while len(florest.queue) > 1:
        t1 = florest.dequeue()
        t2 = florest.dequeue()

        root = Node(t1.weigth + t2.weigth)
        root.left = t1
        root.right = t2
        florest.queue_add(root)

    return florest.dequeue()


def _build_code_table(h_tree, path=""):
    if(not h_tree):
        return {}
    if(h_tree.is_leaf()):
        return {h_tree.data: path}
    return {**_build_code_table(h_tree.left, path + "0"), **_build_code_table(h_tree.right, path + "1")}


def _huffencode(text):
    freqs = _frequency_dictionary(text)
    huff_tree = _build_huff_tree(freqs)
    code_table = _build_code_table(huff_tree)

    encoded_string = ""
    for char in text:
        encoded_string += code_table[char]

    return (encoded_string, code_table)


def _huffdecode(encoded_text, code_table):
    buffer = ""
    decoded_text = ""
    inverse_code = reverse_dict(code_table)
    print(inverse_code)

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

class HuffmanStats(CompressionStats):
    def __init__(self, originaltext, compressedtext, codetable):
        super().__init__(originaltext, compressedtext)
        self.codetable = codetable
        self.avgcode = self._avg_code()
    
    def _avg_code(self):
        super()._avg_code()
        codesizes = list(map(len,  self.codetable.values()))
        return sum(codesizes) / len(codesizes)


class HuffmanCompressor(_TextCompressor):
    def __init__(self, text):
        super().__init__(text)
        self.codetable = {}
        self.encodedtext = ""

    def encode(self):
        super().encode()
        encodedtext, table = _huffencode(self.originaltext)
        self.encodedtext = encodedtext
        self.codetable = table
        self.stats = HuffmanStats(self.originaltext, self.encodedtext, self.codetable)
        print(str(self.stats))

    def decode(self):
        super().decode()
        if self.encodedtext and self.codetable:
            print(_huffdecode(self.encodedtext, self.codetable))
        else:
            raise Exception("No text to decode")
