                      

import argparse
import xml.etree.ElementTree as ET
import re
import math
import sys
from parse_svg_file import parse_svg_file, tag

def dist_point_to_segment(pt, a, b):
\
\
       
    x,y = pt; x1,y1 = a; x2,y2 = b
    dx = x2 - x1; dy = y2 - y1
    if dx==0 and dy==0:
        return math.hypot(x-x1, y-y1)
    t = ((x-x1)*dx + (y-y1)*dy) / (dx*dx + dy*dy)
    t = max(0.0, min(1.0, t))
    proj_x = x1 + t*dx; proj_y = y1 + t*dy
    return math.hypot(x - proj_x, y - proj_y)

def intersect_circle_segment(center, r, p1, p2):
\
\
       
    dx,dy = p2[0]-p1[0], p2[1]-p1[1]
    fx,fy = p1[0]-center[0], p1[1]-center[1]
    a = dx*dx + dy*dy
    b = 2*(fx*dx + fy*dy)
    c = fx*fx + fy*fy - r*r
    disc = b*b - 4*a*c
    if disc < 0:
        return []
    sqrt_disc = math.sqrt(disc)
    t1 = (-b + sqrt_disc) / (2*a)
    t2 = (-b - sqrt_disc) / (2*a)
    pts = []
    for t in (t1, t2):
        if 0 <= t <= 1:
            pts.append((p1[0] + t*dx, p1[1] + t*dy))
    return pts

def circle_circle_intersections(c0, r0, c1, r1):
\
\
       
    dx,dy = c1[0]-c0[0], c1[1]-c0[1]
    d = math.hypot(dx,dy)
    if d > r0+r1 or d < abs(r0-r1) or d == 0:
        return []
    a = (r0*r0 - r1*r1 + d*d) / (2*d)
    h_sq = r0*r0 - a*a
    h = math.sqrt(max(h_sq,0))
    xm = c0[0] + a*(dx/d)
    ym = c0[1] + a*(dy/d)
    rx = -dy*(h/d)
    ry = dx*(h/d)
    return [(xm+rx, ym+ry), (xm-rx, ym-ry)]

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

    out_circs = sorted(out_circs, key=lambda x: x[1])[-3:]

    gt_root  = ET.parse(args.ground_truth).getroot()
    out_root = ET.parse(args.llm_output).getroot()

    tol_center = 1e0
    tol_line   = 1e0

    input_pts = None
    if len(gt_segs) != 2:
        print("0"); sys.exit(0)
    if gt_segs[0][0] == gt_segs[1][0]:
        input_pts = [gt_segs[0][1], gt_segs[0][0], gt_segs[1][1]]
    elif gt_segs[0][1] == gt_segs[1][0]:
        input_pts = [gt_segs[0][0], gt_segs[0][1], gt_segs[1][1]]
    elif gt_segs[0][0] == gt_segs[1][1]:
        input_pts = [gt_segs[0][1], gt_segs[0][0], gt_segs[1][0]]
    elif gt_segs[0][1] == gt_segs[1][1]:
        input_pts = [gt_segs[0][0], gt_segs[0][1], gt_segs[1][0]]

    if not input_pts or len(input_pts) != 3:
        print("0"); sys.exit(0)
    mid_pt = input_pts[1]

    cond1_circle = None
    for c, r in out_circs:
        if math.hypot(c[0]-mid_pt[0], c[1]-mid_pt[1]) <= tol_center:
            cond1_circle = (c, r)
            break
    if cond1_circle is None:
        print("0"); sys.exit(0)

    intersections = []
    for i in range(2):
        seg_p, seg_q = input_pts[i], input_pts[i+1]
        intersections += intersect_circle_segment(cond1_circle[0], cond1_circle[1], seg_p, seg_q)
                         
    if len(intersections) != 2:
        print("0"); sys.exit(0)
    ip1, ip2 = intersections

    cond2 = []
    for ip in (ip1, ip2):
        found = False
        for c, r in out_circs:
            if math.hypot(c[0]-ip[0], c[1]-ip[1]) <= tol_center and r > 10:
                cond2.append((c, r))
                found = True
                break
        if not found:
            print("0"); sys.exit(0)
             
    if abs(cond2[0][1] - cond2[1][1]) > tol_center:
        print("0"); sys.exit(0)
               
    d_centers = math.hypot(cond2[0][0][0]-cond2[1][0][0],
                           cond2[0][0][1]-cond2[1][0][1])
    if not (tol_center < d_centers < 2*cond2[0][1] - tol_center):
        print("0"); sys.exit(0)

    circ_ips = circle_circle_intersections(cond2[0][0], cond2[0][1],
                                           cond2[1][0], cond2[1][1])
    if len(circ_ips) != 2:
        print("0"); sys.exit(0)
                    
    target_ip = min(circ_ips, key=lambda p: math.hypot(p[0]-mid_pt[0], p[1]-mid_pt[1]))

    ok3 = False
    for a,b in out_segs:
        if (dist_point_to_segment(mid_pt, a, b) <= tol_line and
            dist_point_to_segment(target_ip, a, b) <= tol_line):
            ok3 = True
            break
    if not ok3:
        print("0"); sys.exit(0)

    print("1")

if __name__ == '__main__':
    main()
