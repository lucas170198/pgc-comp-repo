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

def _reverse_bootdict(bootdict):
    reversed = {}

    for key, value in bootdict.items():
        reversed[value] = key
    return reversed 


def encode(text):
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

def decode(bootdict, codes):
    codetable = _reverse_bootdict(bootdict)
    decodedtext = ""
    for code in codes:
        decodedtext += codetable[code]
    
    return decodedtext
