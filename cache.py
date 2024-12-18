#!/usr/bin/env python

import sys
import os
from collections import deque

def is_power_of_2(x):
    return (x & (x - 1)) == 0 and x > 0

class Cache:
    def __init__(self, cache_size, block_size, associativity, prefetch_size):
        self.cache_size = cache_size
        self.block_size = block_size
        self.prefetch_size = prefetch_size
        if associativity == 'direct' or associativity == 'assoc':
            self.num_sets = cache_size // block_size
            self.num_ways = 1
        else:
            self.num_ways = int(associativity.split(':')[1])
            self.num_sets = cache_size // (block_size * self.num_ways)
        self.cache = [deque(maxlen=self.num_ways) for _ in range(self.num_sets)]

    def parse_addr(self, addr):
        s = (addr // self.block_size) % self.num_sets
        t = addr // (self.block_size * self.num_sets)
        return (s, t)

    def access(self, addr, op="R"):
        s, t = self.parse_addr(addr)
        for block in self.cache[s]:
            if block['tag'] == t:
                return True

        # FIFO replacement
        if len(self.cache[s]) >= self.num_ways:
            self.cache[s].popleft()
        self.cache[s].append({'tag': t, 'data': None})

        # Prefetch blocks
        if self.prefetch_size > 0:
            for i in range(self.block_size, self.prefetch_size*self.block_size, self.block_size):
                next_set, next_tag = self.parse_addr(addr + i)
                if len(self.cache[next_set]) < self.num_ways:
                    self.cache[next_set].append({'tag': next_tag, 'data': None})
        return False

if __name__ == "__main__":
    if len(sys.argv) != 6:
        print(f"Usage: {sys.argv[0]} <cache size> <block size> <associativity> <prefetch size> <trace file>")
        sys.exit(1)

    cache_size = int(sys.argv[1])
    block_size = int(sys.argv[2])
    associativity = sys.argv[3]
    prefetch_size = int(sys.argv[4])
    trace_file = sys.argv[5]

    if not is_power_of_2(cache_size) or not is_power_of_2(block_size):
        print("Error: Cache size and block size must be powers of 2.")
        sys.exit(1)
    if associativity != "direct" and not associativity.startswith("assoc"):
        print("Error: Invalid associativity.")
        sys.exit(1)
    if not os.path.exists(trace_file):
        print(f"Error: Trace file {trace_file} not found.")
        sys.exit(1)

    hits = 0
    n = 0
    c = Cache(cache_size, block_size, associativity, prefetch_size)

    with open(trace_file, 'r') as trace:
        for line in trace:
            line = line.strip()
            if line:
                op, addr = line.split()
                addr = int(addr, base=16)
                hits += c.access(addr, op)
                n += 1

    print(f"Hits: {hits}, Misses: {n - hits}")
