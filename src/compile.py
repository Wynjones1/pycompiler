#!/usr/bin/env python2.7
import os
import argparse
from   parser  import *
from   os.path import join as pjoin

def main(*args, **kwargs):
    filepath = os.path.dirname(os.path.realpath(__file__))
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("--input", "-i", default = pjoin(filepath, "../tests/lang/simple_0.x"))
    args = argument_parser.parse_args()

    data = open(args.input).read()
    try:
        program = parse(data)
    except ParseError as e:
        print(e)
    program.make_tables()
    program.sema()
    graph = program.output_graph("out.png")

if __name__ == "__main__":
    main()
