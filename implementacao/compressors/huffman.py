from utils import Node, PriorityQueue, _TextCompressor, CompressionMode, reverse_dict
import json
import os


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

    for s in encoded_text:
        symbol = inverse_code[buffer] if buffer in inverse_code else ""
        if(symbol):
            decoded_text = decoded_text + symbol
            buffer = s
        else:
            buffer = buffer + s

    # When buffer is increased on the last iteration
    last_symbol = inverse_code[buffer]
    decoded_text += last_symbol or ""

    return decoded_text

class HuffmanCompressor(_TextCompressor):
    def __init__(self, filename, mode='e'):
        fullpath = os.path.join(os.getcwd(), filename)
        super().__init__(fullpath, mode)
        self.filename = filename
    
    def _opentextfile(self):
        with open(self.fullpath + ".txt", "r") as file:
            self.text = file.read()

    def encode(self):
        if self.compmode is not CompressionMode.ENCODE:
            raise Exception("This method is not allowed on this mode")
        
        self._opentextfile()

        encodedtext, table = _huffencode(self.text)
        with open(self.fullpath + ".huff", "w") as outfile:
            outfile.write(encodedtext)

        with open(self.fullpath + ".meta", "w") as outtable:
            outtable.write(json.dumps(table))

         
    
    def decode(self):
        if self.compmode is not CompressionMode.DECODE:
            raise Exception("This method is note allowed on this mode")
        
        encodedtext = ""
        codetable = {}
        with open(self.fullpath + ".huff", "r") as huff:
            encodedtext = huff.read()
        
        with open(self.fullpath + ".meta", "r") as meta:
            contents = meta.read()
            codetable = json.loads(contents)
        
        print(_huffdecode(encodedtext, codetable))
