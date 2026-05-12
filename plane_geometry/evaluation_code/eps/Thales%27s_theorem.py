                      

import argparse
import xml.etree.ElementTree as ET
import re
import math
import sys
from parse_svg_file import parse_svg_file

def dist_point_to_segment(pt, a, b):
                          
    x,y = pt; x1,y1 = a; x2,y2 = b
    dx, dy = x2-x1, y2-y1
    if dx==0 and dy==0:
        return math.hypot(x-x1, y-y1)
    t = ((x-x1)*dx + (y-y1)*dy) / (dx*dx + dy*dy)
    t = max(0.0, min(1.0, t))
    proj = (x1 + t*dx, y1 + t*dy)
    return math.hypot(x-proj[0], y-proj[1])

def segment_circle_intersect(a, b, center, r, tol=1e0):
                                           
    (x1, y1), (x2, y2) = a, b
    (cx, cy) = center
    dx, dy = x2 - x1, y2 - y1
    A = dx*dx + dy*dy
    B = 2*((x1-cx)*dx + (y1-cy)*dy)
    C = (x1-cx)**2 + (y1-cy)**2 - r*r
    disc = B*B - 4*A*C
    if disc < 0:
        return False
    sqrt_disc = math.sqrt(disc)
    t1 = (-B + sqrt_disc)/(2*A)
    t2 = (-B - sqrt_disc)/(2*A)
                                  
    return (-0.1 <= t1 <= 1.1) and (-0.1 <= t2 <= 1.1)

def intersect_segments(p1, p2, p3, p4, tol=1e0):
                                             
    x1,y1 = p1; x2,y2 = p2; x3,y3 = p3; x4,y4 = p4
    denom = (x1-x2)*(y3-y4) - (y1-y2)*(x3-x4)
    if abs(denom) < tol:
        return None
    px = ((x1*y2 - y1*x2)*(x3-x4) - (x1-x2)*(x3*y4 - y3*x4)) / denom
    py = ((x1*y2 - y1*x2)*(y3-y4) - (y1-y2)*(x3*y4 - y3*x4)) / denom
              
    def within(a, b, v):
        return min(a, b) - tol <= v <= max(a, b) + tol
    if within(x1, x2, px) and within(y1, y2, py) and within(x3, x4, px) and within(y3, y4, py):
        return (px, py)
    return None

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

    segs_sorted = sorted(
    out_segs,
    key=lambda seg: math.hypot(seg[1][0] - seg[0][0], seg[1][1] - seg[0][1]),
    reverse=True
    )
    out_segs = segs_sorted[:3]

    if len(gt_circs) != 1:
        print("0"); return
    center, radius = gt_circs[0]

    if len(out_segs) < 3:
        print("0"); return

    cyl_segs = [seg for seg in out_segs if segment_circle_intersect(seg[0], seg[1], center, radius)]
    if len(cyl_segs) != 3:
        print("0"); return

    passes_center = any(
        dist_point_to_segment(center, seg[0], seg[1]) <= 1e0
        for seg in cyl_segs
    )
    if not passes_center:
        print("0"); return

    pts = []
    for i in range(3):
        for j in range(i+1, 3):
            ip = intersect_segments(cyl_segs[i][0], cyl_segs[i][1],
                                     cyl_segs[j][0], cyl_segs[j][1])
            if ip is None:
                print("0"); return
            pts.append(ip)
             
    if len(pts) != 3:
        print("0"); return
             
    for (x,y) in pts:
        if abs(math.hypot(x-center[0], y-center[1]) - radius) > 5e0:
            print("0"); return

    print("1")

if __name__ == '__main__':
    main()