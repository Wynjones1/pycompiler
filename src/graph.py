#!/usr/bin/env python2.7
import pydot

class Graph(object):
    def __init__(self):
        self.graph= pydot.Dot(graph_type = "digraph")
        self.nodes = []
        self.edges = []

    def add_node(self, name, shape = "box"):
        node = pydot.Node(len(self.nodes),
                          label = '"{}"'.format(name),
                          shape=shape)
        self.nodes.append(node)
        self.graph.add_node(self.nodes[-1])
        return len(self.nodes) - 1

    def add_edge(self, index0, index1, label = ""):
        edge = pydot.Edge(self.nodes[index0],
                          self.nodes[index1],
                          label = '"{}"'.format(label))
        self.edges.append(edge)
        self.graph.add_edge(self.edges[-1])
        return len(self.edges) - 1

    def output(self, filename):
        self.graph.write_png(filename)

def main():
    g = Graph()
    some = """\
    some really long paragraph
    that keeps going on and on
    and on and on and on.
    """

    g.add_node("node0")
    g.add_node("node1")
    g.add_edge(0, 1, "edge 1")
    g.output("out.png")
if __name__ == "__main__":
    main()
