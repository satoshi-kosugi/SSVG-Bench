                      

import argparse
import xml.etree.ElementTree as ET
from parse_svg_file import parse_svg_file
import networkx as nx

def main():
    p = argparse.ArgumentParser(description="SVG 出力評価スクリプト")
    p.add_argument('ground_truth', help="正解 SVG のファイルパス")
    p.add_argument('llm_output',   help="LLM 出力 SVG のファイルパス")
    args = p.parse_args()

    gt_G = parse_svg_file(args.ground_truth)
    out_G = parse_svg_file(args.llm_output)

    node_match = lambda n1, n2: n1['fill'] == n2['fill']

    iso = nx.is_isomorphic(gt_G, out_G, node_match=node_match)

    print("1" if iso else "0")

if __name__ == '__main__':
    main()
