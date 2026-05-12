import argparse
import re
import math
import random
import sys
import os
import networkx as nx

from parse_tikz_file import parse_tikz_file
from parse_svg_file import parse_svg_file

if __name__ == '__main__':
    p = argparse.ArgumentParser(description="TikZ evaluation script")
    p.add_argument('ground_truth', help="Ground-truth .svg file path")
    p.add_argument('llm_output',   help="LLM output .svg file path")
    args = p.parse_args()

    gt_G  = parse_svg_file(args.ground_truth)
    out_G = parse_tikz_file(args.llm_output)

    node_match = lambda n1, n2: n1['fill'] == n2['fill']

    iso = nx.is_isomorphic(gt_G, out_G, node_match=node_match)

    print("1" if iso else "0")
