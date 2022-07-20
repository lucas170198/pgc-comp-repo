from compressors.utils import _TextCompressor, CompressionStats, reverse_dict
from functools import reduce

# TODO: Review lzw implementaion, seems to me not very efficiecy when count the code table
class EncriptyTable:
    def __init__(self, text):
        symbols = set(text)
        self.size = len(symbols)
        self.bootdict = dict([(symbol, code) for code, symbol in enumerate(symbols)])
    

    def has_symbol(self, symbol):
        return symbol in self.bootdict
    
    def add_symbol(self, symbol):
        if not self.has_symbol(symbol):
            code = self.size
            self.bootdict[symbol] = code
            self.size += 1
            return code
        else:
            raise Exception("Symbol " +  symbol + " already on the table")
    
    def get_code(self, symbol):
        return self.bootdict[symbol]


def _lzw_encode(text):
    table = EncriptyTable(text)
    code = []
    wbegin = 0
    wend = 1

    while wend < len(text):
        text_seq = text[wbegin:wend+1]

        if table.has_symbol(text_seq):
            wend += 1
            continue

        table.add_symbol(text_seq)
        code.append(table.get_code(text_seq[:-1]))
        wbegin = wend
        wend += 1
    return (table.bootdict, code)

def _lzw_decode(bootdict, codes):
    code_table = reverse_dict(bootdict)
    decoded_text = ""
    for code in codes:
        decoded_text += code_table[code]
    
    return decoded_text

class LzwStats(CompressionStats):
    def _calculate_table_size(self, code_table):
        INT_BYTES_SIZE = 4
        keys_bytes_size = len(reduce(lambda x, y: x + y, code_table.keys(), ""))
        values_bytes_size = len(code_table) * INT_BYTES_SIZE
        return keys_bytes_size + values_bytes_size

    def __init__(self, original_text, compressed_text, code_table):
        code_table_size  = self._calculate_table_size(code_table)
        self.compressedtextsize = len(compressed_text) + code_table_size
        self.originaltextsize = len(original_text)

class LzwCompressor(_TextCompressor):
    def __init__(self):
        super().__init__()
        self.codetable = {}
        self.encodedbytes = []
    
    def encode(self, text):
        super().encode(text)
        bootdict, encoded = _lzw_encode(self.originaltext)
        self.codetable = bootdict
        self.encodedbytes = encoded
        self.stats = LzwStats(self.originaltext, self.encodedbytes, self.codetable)
        print(str(self.stats))
    
    def decode(self):
        super().decode()
        if self.encodedbytes and self.codetable:
            print(_lzw_decode(self.codetable, self.encodedbytes))
        else:
            raise Exception("No text to decode")