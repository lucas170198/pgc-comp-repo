from enum import Enum

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

    # TODO: Implement print inorder
    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return "NodeClass(data=" + str(self.data) + ", w=" + str(self.weigth) + ")"


# ################### Heap Priprity queue
def _maxheapfy_bottomup(heap, pos):
    newitem = heap[pos]

    while pos > 0:
        parentpos = (pos - 1) // 2
        parent = heap[parentpos]
        if parent > newitem:
            heap[pos] = parent
            pos = parentpos
            continue
        break
    heap[pos] = newitem


def _maxheapfy_topdown(heap):
    endpos = len(heap)
    pos = 0
    newitem = heap[pos]

    childpos = 2*pos + 1    # leftmost child position
    while childpos < endpos:
        # Set childpos to index of greater child
        rightpos = childpos + 1
        if rightpos < endpos and heap[childpos] < heap[rightpos]:
            childpos = rightpos

        heap[pos] = heap[childpos]
        pos = childpos
        childpos = 2*pos + 1

    # The leaf at pos is empty now.  Put newitem there, and bubble it up
    # to its final resting place (by sifting its parents down).
    heap[pos] = newitem
    _maxheapfy_bottomup(heap, pos)


def heappush(heap, item):
    heap.append(item)
    _maxheapfy_bottomup(heap, len(heap) - 1)


def heappop(heap):
    lastitem = heap.pop()
    if heap:
        head = heap[0]
        heap[0] = lastitem
        _maxheapfy_topdown(heap)
        return head
    return lastitem


class PriorityQueue:
    def __init__(self):
        self.queue = []

    def queue_add(self, elem):
        heappush(self.queue, elem)

    def dequeue(self):
        if not self.is_empty():
            return heappop(self.queue)

    def is_empty(self):
        return not self.queue

# Compressor utils
# TODO: use list conprehension


def reverse_dict(dict):
    reversed = {}
    for key, value in dict.items():
        reversed[value] = key
    return reversed

stats_text = """Average code size: {csize}
Orignal size (byte): {osize}
New size (bytes): {nsize}
Compression rate (%): {crate}"""

class CompressionStats:

    def _avg_code(self):
        pass
        
    def _compression_rate(self):
        return 100 - (self.compressedtextsize / self.originaltextsize) * 100

    def __init__(self, originaltext, compressedtext):
        self.originaltextsize = len(originaltext)
        self.compressedtextsize = len(compressedtext) // 8

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
