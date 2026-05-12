                      

import argparse
import xml.etree.ElementTree as ET
import re
import math
import sys
import itertools
from parse_svg_file import parse_svg_file

def dist_point_to_segment(pt, a, b):
    x,y = pt; x1,y1 = a; x2,y2 = b
    dx = x2 - x1; dy = y2 - y1
    if dx==0 and dy==0:
        return math.hypot(x-x1, y-y1)
    t = ((x-x1)*dx + (y-y1)*dy) / (dx*dx + dy*dy)
    t = max(0.0, min(1.0, t))
    proj_x = x1 + t*dx; proj_y = y1 + t*dy
    return math.hypot(x - proj_x, y - proj_y)

def match_segments(gt_segs, out_segs, tol=1e1):
                                         
    for (p1,p2) in gt_segs:
        ok = False
        for (q1,q2) in out_segs:
            if dist_point_to_segment(p1, q1, q2) <= tol and dist_point_to_segment(p2, q1, q2) <= tol:
                ok = True; break
        if not ok:
            return False
    return True

def external_tangents(c1, r1, c2, r2):
                             
    (x1,y1), (x2,y2) = c1, c2
    dx = x2 - x1; dy = y2 - y1
    d2 = dx*dx + dy*dy
    if d2 <= (r1 - r2)**2:
        return []
    d = math.sqrt(d2)
    a = (r1 - r2) / d
    a = max(-1.0, min(1.0, a))
    b = math.sqrt(max(0.0, 1 - a*a))
    ux = dx / d; uy = dy / d
    vx = -dy / d; vy = dx / d
    n1 = (a*ux + b*vx, a*uy + b*vy)
    n2 = (a*ux - b*vx, a*uy - b*vy)
    p11 = (x1 + r1 * n1[0], y1 + r1 * n1[1])
    p12 = (x2 + r2 * n1[0], y2 + r2 * n1[1])
    p21 = (x1 + r1 * n2[0], y1 + r1 * n2[1])
    p22 = (x2 + r2 * n2[0], y2 + r2 * n2[1])
    return [(p11, p12), (p21, p22)]

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

    if len(gt_circs) < 5:
        print("0"); sys.exit(0)
    gt_circs_sorted = sorted(gt_circs, key=lambda x: x[1])[:4]

    tol = 1e1
    ok_all = True
    for (c1, r1), (c2, r2) in itertools.combinations(gt_circs_sorted, 2):
        tangents = external_tangents(c1, r1, c2, r2)
        if not tangents:
            ok_all = False; break
                              
        if not any(match_segments([seg], out_segs, tol) for seg in tangents):
            ok_all = False; break

    print("1" if ok_all else "0")

if __name__ == '__main__':
    main()