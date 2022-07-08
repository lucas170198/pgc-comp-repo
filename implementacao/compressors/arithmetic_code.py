from decimal import Decimal
from compressors.utils import _TextCompressor, CompressionStats, frequency_dictionary
from functools import reduce

def _single_value_encoded(last_interval_prob):
    "Define the final encoded value, using the last iteration result"
    all_probs = reduce(lambda x, y : x + list(y) , last_interval_prob.values(), [])
    max_prob = max(all_probs)
    min_prob = min(all_probs)

    return (max_prob + min_prob) / 2

def _proccess_intervals(prob_table, curr_min, curr_max):
    "Decide in with interval a symbol is inserted according with the current limits"
    
    prob_ranges = {}
    line_range = curr_max - curr_min

    for term, prob in prob_table.items():
        actual_prob = (prob * line_range) + curr_min
        prob_ranges[term] = [curr_min, actual_prob]
        curr_min = actual_prob

    return prob_ranges

def _probability_table(text):
    "Build a table with the frequency of each char in the msg"
    freqdict = frequency_dictionary(text)
    totalsymbols = len(text)
    table = {}
    for k, v in freqdict.items():
        table[k] = Decimal(v / totalsymbols)
    
    return table


def _ac_encode(text):
    prob_table = _probability_table(text)

    curr_min_interval = Decimal(0.0)
    curr_max_interval = Decimal(1.0)

    #Proccess each char to restring the actual limits
    for symbol in text:
        interval_prob = _proccess_intervals(prob_table, curr_min_interval, curr_max_interval)
        print(symbol)     
        curr_min_interval = interval_prob[symbol][0]
        curr_max_interval = interval_prob[symbol][1]
    
    last_interval_prob = _proccess_intervals(prob_table, curr_min_interval, curr_max_interval)

    encoded_value = _single_value_encoded(last_interval_prob)

    return encoded_value, prob_table, len(text)

def _ac_decode(encoded_value, prob_table, original_text_size):
    decoded_text = ""
    curr_min_interval = Decimal(0.0)
    curr_max_interval = Decimal(1.0)

    for _ in range(original_text_size):
        interval_prob = _proccess_intervals(prob_table, curr_min_interval, curr_max_interval)
        
        #find the item inside of actual probability range
        for symbol, interval in interval_prob.items():
            if encoded_value >= interval[0] and encoded_value <= interval[1]:
                break
        
        decoded_text += symbol
        curr_min_interval = interval_prob[symbol][0]
        curr_max_interval = interval_prob[symbol][1]
    
    return decoded_text