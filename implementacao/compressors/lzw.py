from compressors.utils import _TextCompressor, CompressionStats, reverse_dict

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
            raise Exception("Symbol" +  symbol + "allready on table")
    
    def get_code(self, symbol):
        return self.bootdict[symbol]


def _lzw_encode(text):
    table = EncriptyTable(text)
    code = []
    wbegin = 0
    wend = 1

    while wend < len(text):
        textseq = text[wbegin:wend+1]

        if table.has_symbol(textseq):
            wend += 1
            continue

        table.add_symbol(textseq)
        code.append(table.get_code(textseq[:-1]))
        wbegin = wend
        wend += 1
    return (table.bootdict, code)

def _lzw_decode(bootdict, codes):
    codetable = reverse_dict(bootdict)
    decodedtext = ""
    for code in codes:
        decodedtext += codetable[code]
    
    return decodedtext

#TODO: Count the code table also
class LzwStats(CompressionStats):
    def __init__(self, originaltext, compressedtext, codetable):
        super().__init__(originaltext, compressedtext)
        self.codetable = codetable

class LzwCompressor(_TextCompressor):
    def __init__(self, text):
        super().__init__(text)
        self.codetable = {}
        self.encodedbytes = []
    
    def encode(self):
        super().encode()
        bootdict, encoded = _lzw_encode(self.originaltext)
        self.codetable = bootdict
        self.encodedbytes = bytearray(encoded)
        self.stats = LzwStats(self.originaltext, self.encodedbytes, self.codetable)
        print(str(self.stats))
    
    def decode(self):
        super().decode()
        if self.encodedbytes and self.codetable:
            print(_lzw_decode(self.codetable, self.encodedbytes))
        else:
            raise Exception("No text to decode")