                      

import argparse
import xml.etree.ElementTree as ET
import re
import math
import sys
from itertools import combinations
from parse_svg_file import parse_svg_file

def length(a, b):
                  
    return math.hypot(a[0]-b[0], a[1]-b[1])

def is_triangle(segments, tol=1e0):
\
\
\
\
       
    pts = []
    for a, b in segments:
        pts.append(a)
        pts.append(b)
    unique = list({tuple(p): p for p in pts}.values())
    if len(unique) != 3:
        return False
                
    deg = {tuple(p): 0 for p in unique}
    for a, b in segments:
        deg[tuple(a)] += 1
        deg[tuple(b)] += 1
    return all(d == 2 for d in deg.values())

def find_matching_triangle(gt_segs, out_segs, tol_len=1e-1):
\
\
\
\

    gt_lens = sorted([length(a,b) for a,b in gt_segs])
                     
    for combo in combinations(out_segs, 3):
        if not is_triangle(combo):
            continue
        out_lens = sorted([length(a,b) for a,b in combo])
        if all(abs(o - g) <= tol_len for o, g in zip(out_lens, gt_lens)):
            return True
    return False

def main():
    p = argparse.ArgumentParser(description="SVG 出力評価スクリプト")
    p.add_argument('ground_truth', help="正解 SVG のファイルパス")
    p.add_argument('llm_output',   help="LLM 出力 SVG のファイルパス")
    args = p.parse_args()

    try:
        gt_segs, gt_circs, gt_ells = parse_svg_file(args.ground_truth, filter_class='output_object')
        out_segs, out_circs, out_ells = parse_svg_file(args.llm_output, filter_class='output_object')
    except Exception:
        print("0")
        sys.exit(0)

    if len(gt_segs) < 3:
        print("0")
        sys.exit(0)

    ok = find_matching_triangle(gt_segs, out_segs, tol_len=1e-1)
    print("1" if ok else "0")

if __name__ == '__main__':
    main()