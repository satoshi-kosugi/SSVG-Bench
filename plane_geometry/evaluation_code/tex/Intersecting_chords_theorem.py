                      

import argparse
import xml.etree.ElementTree as ET
import re
import math
import sys
from parse_svg_file import parse_svg_file

def seg_circle_intersections(a, b, center, r, tol=1e0):

    (x1, y1), (x2, y2) = a, b
    (cx, cy) = center
    dx, dy = x2-x1, y2-y1
    fx, fy = x1-cx, y1-cy
    A = dx*dx + dy*dy
    B = 2*(fx*dx + fy*dy)
    C = fx*fx + fy*fy - (r - tol)**2
    disc = B*B - 4*A*C
    if disc < 0:
        return 0
    disc_sqrt = math.sqrt(disc)
    t1 = (-B + disc_sqrt) / (2*A)
    t2 = (-B - disc_sqrt) / (2*A)
    cnt = 0
    for t in (t1, t2):
        if 0 <= t <= 1:
            cnt += 1
    return cnt

def line_intersection(p1, p2, p3, p4):
                                              
    x1,y1 = p1; x2,y2 = p2; x3,y3 = p3; x4,y4 = p4
    denom = (x1-x2)*(y3-y4) - (y1-y2)*(x3-x4)
    if abs(denom) < 1e0:
        return None
    px = ((x1*y2 - y1*x2)*(x3-x4) - (x1-x2)*(x3*y4 - y3*x4)) / denom
    py = ((x1*y2 - y1*x2)*(y3-y4) - (y1-y2)*(x3*y4 - y3*x4)) / denom
    return (px, py)

def main():
    p = argparse.ArgumentParser(description="SVG 出力評価スクリプト")
    p.add_argument('ground_truth', help="正解 SVG のファイルパス")
    p.add_argument('llm_output',   help="LLM 出力 SVG のファイルパス")
    args = p.parse_args()

    try:
        gt_segs, gt_circs, gt_ells = parse_svg_file(args.ground_truth, filter_class='input_object')
        out_segs, out_circs, out_ells = parse_svg_file(args.llm_output, filter_class='output_object')
    except Exception:
        print("0")
        sys.exit(0)

    if len(gt_circs) != 1:
        print("0"); sys.exit(0)
    center, r = gt_circs[0]

    through = [s for s in out_segs if seg_circle_intersections(s[0], s[1], center, r) == 2]
    if len(through) != 2:
        print("0"); sys.exit(0)

    inter = line_intersection(through[0][0], through[0][1], through[1][0], through[1][1])
    if inter is None:
        print("0"); sys.exit(0)

    d = math.hypot(inter[0]-center[0], inter[1]-center[1])
    tol = r * 0.05                
    if d <= r + tol:
        print("1")
    else:
        print("0")

if __name__ == '__main__':
    main()