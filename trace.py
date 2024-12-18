#!/usr/bin/env python
from sys import argv
from random import randrange

if __name__ == "__main__":
    if len(argv) != 3:
        print(f"Usage {argv[0]} <n> <file name>")
        exit(1)

    n = int(argv[1], base=10)
    with open(argv[2], "w") as f:
        for i in range(n):
            rw = "R" if randrange(2) else "W"
            addr = hex(randrange(2**32))
            f.write(f"{rw} {addr}\n")
