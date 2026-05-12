                      
                       
import argparse
import networkx as nx

from parse_eps_file import parse_eps_file
from parse_svg_file import parse_svg_file

def hex_difference(hex_code1, hex_code2):
    hex_code1 = hex_code1.lstrip('#')
    rgb1 = tuple(int(hex_code1[i:i+2], 16) for i in (0, 2, 4))
    hex_code2 = hex_code2.lstrip('#')
    rgb2 = tuple(int(hex_code2[i:i+2], 16) for i in (0, 2, 4))
    return abs(rgb1[0] - rgb2[0]) + abs(rgb1[1] - rgb2[1]) + abs(rgb1[2] - rgb2[2])

if __name__ == '__main__':
    p = argparse.ArgumentParser(description="EPS evaluation script")
    p.add_argument('ground_truth', help="Ground-truth .svg file path")
    p.add_argument('llm_output',   help="LLM output .svg file path")
    args = p.parse_args()

    gt_G  = parse_svg_file(args.ground_truth)
    out_G = parse_eps_file(args.llm_output)

    node_match = lambda n1, n2: hex_difference(n1['fill'], n2['fill']) < 5

    iso = nx.is_isomorphic(gt_G, out_G, node_match=node_match)

    print("1" if iso else "0")
