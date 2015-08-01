#!/usr/bin/env python2.7
import os
from parse import *

class TacState(object):
    def __init__(self):
        self._label_count = 0
        self._temp_count  = 0

    def get_temp(self):
        out = self._temp_count
        self._temp_count += 1
        return out

    def get_label(self):
        out = self._label_count
        self._label_count += 1
        return out
        

class TAC:
    pass

class Assign(TAC):
    pass

if __name__ == "__main__":
    test = """
    function a()
    {
        while(a < 10)
        {
            b := 10 + 10
        }
    }
    """
    prog = parse(test)
    prog.make_tac(TacState())

    """
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("--input", "-i",
                                 default = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                        "tests", "lang", "simple_0.x"))
    args = argument_parser.parse_args()

    data = open(args.input).read()
    program = parse(data)
    """
