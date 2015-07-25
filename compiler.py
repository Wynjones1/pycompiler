#!/usr/bin/env python2.7
from lexer  import *
from parser import *

if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("--input", "-i",
                                 default = "tests/lang/simple_0.x")
    args = argument_parser.parse_args()

    data = open(args.input).read()
    program = parse(data)
    program.make_tables()
    graph = program.output_graph("out.png")
