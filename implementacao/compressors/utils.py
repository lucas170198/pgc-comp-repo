# Tree implementation
class Node:
    def __init__(self, weigth, data=''):
        self.left = None
        self.right = None
        self.data = data
        self.weigth = weigth

    def __lt__(self, other):
        return self.weigth < other.weigth

    def is_leaf(self):
        return (not self.left) and (not self.right)



# Ref: https://stackoverflow.com/questions/34012886/print-binary-tree-level-by-level-in-python
def print_tree(node, level=0):
    if node != None:
        print_tree(node.left, level + 1)
        print(' ' * 10 * level + '-> ' + "(" + node.data + "," + str(node.weigth) + ")")
        print_tree(node.right, level + 1)

# Compressor utils
def reverse_dict(dict):
    reversed = {}
    for key, value in dict.items():
        reversed[value] = key
    return reversed

def frequency_dictionary(text):
    freqs = {}
    for character in text:
        freqs[character] = freqs.get(character, 0) + 1
        
    return freqs

stats_text = """Average code size: {csize}
Orignal size (bytes): {osize}
New size (bytes): {nsize}
Compression rate (%): {crate}"""

class CompressionStats:

    def _avg_code(self):
        return (self.compressedtextsize / self.originaltextsize) * 8
        
    def _compression_rate(self):
        return 100 - (self.compressedtextsize / self.originaltextsize) * 100

    def __init__(self, originaltext, compressedtext):
        self.originaltextsize = len(originaltext)
        self.compressedtextsize = len(compressedtext)

    def __str__(self) -> str:
        return stats_text.format(csize=self._avg_code(), osize=self.originaltextsize, nsize=self.compressedtextsize, crate=self._compression_rate())

class _TextCompressor:
    def __init__(self, text):
        self.originaltext = text
        self.stats = None

    def encode(self):
        if not self.originaltext:
            raise Exception("No text to encode")
        pass

    def decode(self):
        pass
