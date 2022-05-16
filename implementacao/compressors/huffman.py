from utils import Node


def _frequency_dictionary(text):
    freqs = {}
    for character in text:
        if character in freqs:
            freqs[character] += 1
        else:
            freqs[character] = 1
    return freqs


def _build_huff_tree(text_freq):
    florest = []

    # Building florest
    for data, weigth in text_freq.items():
        root = Node(weigth, data)
        florest.append(root)

    # TODO: Build an HeapQ to a more efficient, the Timsort is n log n
    florest.sort(reverse=True)  # Transform it on a priority key

    while len(florest) > 1:
        t1 = florest.pop()
        t2 = florest.pop()

        root = Node(t1.weigth + t2.weigth)
        root.left = t1
        root.right = t2
        florest.append(root)
        florest.sort()

    return florest[0]


def _build_code_table(h_tree, path=""):
    if(not h_tree):
        return {}
    if(h_tree.is_leaf()):
        return {h_tree.data: path}
    return {**_build_code_table(h_tree.left, path + "0"), **_build_code_table(h_tree.right, path + "1")}


def encode(text):
    freqs = _frequency_dictionary(text)
    huff_tree = _build_huff_tree(freqs)
    code_table = _build_code_table(huff_tree)

    encoded_string = ""
    for char in text:
        encoded_string += code_table[char]

    return (encoded_string, code_table)


def reverse_code_table(code_table):
    reversed = {}
    for key, value in code_table.items():
        reversed[value] = key
    return reversed


def decode(encoded_text, code_table):
    buffer = ""
    decoded_text = ""
    inverse_code = reverse_code_table(code_table)

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


encoded_tuple = encode("aaa bb")
print(decode(encoded_tuple[0], encoded_tuple[1]))
