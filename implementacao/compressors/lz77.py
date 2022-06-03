from curses import window
from typing import Tuple, NewType


Token = NewType("TokenType", Tuple[int, int, str])

def token_is_null(token):
    return not (token[0] or token[1])

def _find_first_match(dictionary, target):
    start = 0
    end = len(target) - 1

    while end < len(dictionary):
        if dictionary[start:end+1] == target:
            return start
        start += 1
        end += 1
    

def _find_best_match_seq(dictionary, lookaheadbuffer):
    
    labpointer = 0
    besttoken = Token((0, 0, lookaheadbuffer[0]))

    while labpointer < len(lookaheadbuffer):
        matchpointer = _find_first_match(dictionary, lookaheadbuffer[:labpointer+1])

        if not matchpointer:
            return besttoken
        
        labpointer += 1
        gobackpointer = len(dictionary) - matchpointer
        besttoken = Token((gobackpointer, labpointer, ""))
    
    return besttoken


def encode(text):
    window = 0
    encoded_dict = []

    while window < len(text):
        token = _find_best_match_seq(dictionary=text[:window], lookaheadbuffer=text[window:])
        encoded_dict.append(token)
        if not token_is_null(token):
            _, size, _ = token
            window += size
            continue
        
        window += 1
    
    return encoded_dict

def decode(tokens):
    decodedtoken = ""
    for token in tokens:
        lookahead, size, char = token
        if token_is_null(token):
            decodedtoken += char
            continue
        subtstrstart = len(decodedtoken) - lookahead
        substrend = subtstrstart + size
        decodedtoken += decodedtoken[subtstrstart:substrend]

    return decodedtoken

"Meu comp"