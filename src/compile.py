#!/usr/bin/env python2.7
import os
import argparse
import syntax_tree as ast
from   parse import *
from   os.path import join as pjoin
import tac

def main(*args, **kwargs):
    default_file = "single_function.x"
    default_file = "simple_0.x"
    filepath = os.path.dirname(os.path.realpath(__file__))
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("--input", "-i", default = pjoin(filepath, "../tests/lang/" + default_file))
    args = argument_parser.parse_args()

    data = open(args.input).read()
    try:
        program = parse(data)
    except ParseError as e:
        print(e)
    program.make_tables()
    try:
        program.sema()
    except ast.SemaError as e:
        print(e)
        print(e.ast._end_token.highlight(5, 5))
        raise
    except KeyError as e:
        print(e)
        #print(e.ast._start_token.highlight(5, 5))
        print(e.ast._end_token.highlight(5, 5))
        raise
    t = program.make_tac(tac.TacState())
    for x in t:
        print(x)
    graph = program.output_graph("out.png")

if __name__ == "__main__":
    main()
