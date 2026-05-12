                      

import argparse
import xml.etree.ElementTree as ET
import re
import math
import sys
from parse_svg_file import parse_svg_file

def dist_point_to_line(pt, a, b):
                        
    x, y = pt
    x1, y1 = a
    x2, y2 = b
    dx = x2 - x1
    dy = y2 - y1
    if dx == 0 and dy == 0:
        return float('inf')
    return abs(dy*x - dx*y + x2*y1 - y2*x1) / math.hypot(dx, dy)

def line_circle_intersections(p1, p2, center, r, tol=1e-0):
                      
    x1, y1 = p1
    x2, y2 = p2
    cx, cy = center
    dx = x2 - x1; dy = y2 - y1
    A = dx*dx + dy*dy
    B = 2*(dx*(x1-cx) + dy*(y1-cy))
    C = (x1-cx)**2 + (y1-cy)**2 - r*r
    disc = B*B - 4*A*C
    if disc < -tol:
        return []
    disc = max(disc, 0)
    sqrt_d = math.sqrt(disc)
    t1 = (-B + sqrt_d) / (2*A)
    t2 = (-B - sqrt_d) / (2*A)
    P1 = (x1 + t1*dx, y1 + t1*dy)
    P2 = (x1 + t2*dx, y1 + t2*dy)
    if disc < tol:
        return [P1]
    return [P1, P2]

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

    if len(gt_segs) != 1 or len(gt_circs) != 1:
        print("0")
        sys.exit(0)
    seg_gt = gt_segs[0]
    circ_gt = gt_circs[0]

    m = ((seg_gt[0][0] + seg_gt[1][0]) / 2, (seg_gt[0][1] + seg_gt[1][1]) / 2)
    center_gt, r_gt = circ_gt

    tol_mid = 1e1
    candidates = []
    for p1, p2 in out_segs:
        if dist_point_to_line(m, p1, p2) <= tol_mid:
            pts = line_circle_intersections(p1, p2, center_gt, r_gt)
            if len(pts) >= 2 and math.hypot(pts[0][0]-pts[1][0], pts[0][1]-pts[1][1]) > tol_mid:
                candidates.append((p1, p2, pts))
              
    unique = []
    for p1, p2, pts in candidates:
        dx = p2[0]-p1[0]; dy = p2[1]-p1[1]
        mag = math.hypot(dx, dy)
        if mag == 0: continue
        ux, uy = dx/mag, dy/mag
        new = True
        for q1, q2, _ in unique:
            vx = q2[0]-q1[0]; vy = q2[1]-q1[1]
            vmag = math.hypot(vx, vy)
            if vmag == 0: continue
            vxu, vyu = vx/vmag, vy/vmag
            if abs(abs(ux*vxu + uy*vyu) - 1) < 0.01:
                new = False; break
        if new:
            unique.append((p1, p2, pts))
    if len(unique) < 2:
        print("0")
        sys.exit(0)

    _, _, pts1 = unique[0]
    _, _, pts2 = unique[1]
    A, B = pts1[0], pts1[1]
    C, D = pts2[0], pts2[1]

    def exists_line(p, q):
        for r1, r2 in out_segs:

            if dist_point_to_line(p, r1, r2) <= tol_mid and dist_point_to_line(q, r1, r2) <= tol_mid:
                return True
        return False

    if (exists_line(A, D) and exists_line(B, C)) or (exists_line(A, C) and exists_line(B, D)):
        print("1")
    else:
        print("0")

if __name__ == '__main__':
    main()