#! /usr/bin/env python
import sys
import timeit

modules = ['green_threads', 'multi_threaded', 'single_threaded']

def main(repeat=3):
    for module in modules:
        timer = timeit.Timer(
            setup='from {} import main'.format(module),
            stmt='main()')
        results = timer.repeat(repeat=repeat, number=1)
        print '{0}: best - {1}'.format(module, min(results))

if __name__ == '__main__':
    repeat = 2
    if len(sys.argv) > 1:
        repeat = int(sys.argv[1])
    main(repeat)