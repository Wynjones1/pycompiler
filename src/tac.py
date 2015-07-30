#!/usr/bin/env python2.7
import os

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
    prog.make_tac(0, 0)

    """
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("--input", "-i",
                                 default = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                        "tests", "lang", "simple_0.x"))
    args = argument_parser.parse_args()

    data = open(args.input).read()
    program = parse(data)
    """
