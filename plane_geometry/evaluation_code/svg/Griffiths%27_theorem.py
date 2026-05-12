                      

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

def match_segments(gt_segs, out_segs, tol=1e1):
                                       
    for (p1,p2) in gt_segs:
        ok = False
        for (q1,q2) in out_segs:
            if dist_point_to_segment(p1, q1, q2) <= tol and\
               dist_point_to_segment(p2, q1, q2) <= tol:
                ok = True
                break
        if not ok:
            return False
    return True

def match_circles(gt_circs, out_circs, tol_center=5, tol_radius=5):
\
\
\
\
\

    target_center = None
    for (c_gt, r_gt) in gt_circs:
        if abs(r_gt - 2.0) <= tol_radius:
            target_center = c_gt
            break
    if target_center is None:
                             
        return False

    count = 0
    for (c_out, r_out) in out_circs:
               
        dc = math.hypot(c_out[0] - target_center[0],
                        c_out[1] - target_center[1])
                                  
        if abs(dc - r_out) <= tol_radius:
            count += 1
    return (count >= 2)

def merge_collinear_segments(segments, angle_tol=math.radians(5)):
\
\
\
       
    merged = []
    thresh = -math.cos(angle_tol)                                                         
    n = len(segments)
    for i in range(n):
        u,v = segments[i]
        for j in range(i+1, n):
            w,x = segments[j]
            shared = None
                    
            if u == w:
                shared, p1, p2 = u, v, x
            elif u == x:
                shared, p1, p2 = u, v, w
            elif v == w:
                shared, p1, p2 = v, u, x
            elif v == x:
                shared, p1, p2 = v, u, w
            else:
                continue
                  
            vec1 = (p1[0]-shared[0], p1[1]-shared[1])
            vec2 = (p2[0]-shared[0], p2[1]-shared[1])
            n1 = math.hypot(*vec1); n2 = math.hypot(*vec2)
            if n1==0 or n2==0:
                continue
            cos_ang = (vec1[0]*vec2[0] + vec1[1]*vec2[1]) / (n1*n2)
            if cos_ang <= thresh:
                merged.append((p1, p2))
    return merged

def dist_point_to_line(pt, a, b):
                                          
    x0, y0 = pt
    x1, y1 = a
    x2, y2 = b
    dx, dy = x2 - x1, y2 - y1
                          
    denom = math.hypot(dx, dy)
    if denom == 0.0:
        return float('inf')

    num = abs(dy * x0 - dx * y0 + (dx * y1 - dy * x1))
    return num / denom

def filter_circles_intersecting_all_lines(gt_segs, out_circs, tol=1):
\
\
\
\
\
\
\
       
    filtered = []
    for (c, r) in out_circs:
        cx, cy = c
        ok = True
        for (a, b) in gt_segs:
            x1, y1 = a
            x2, y2 = b
            dx, dy = x2 - x1, y2 - y1

            if dx == 0.0 and dy == 0.0:
                                           
                if abs(math.hypot(cx - x1, cy - y1) - r) > tol:
                    ok = False
                    break
            else:
                                                    
                d = dist_point_to_line((cx, cy), a, b)
                if d > r + tol:
                    ok = False
                    break

        if ok:
            filtered.append((c, r))
    return filtered

def main():
    p = argparse.ArgumentParser(description="SVG 出力評価スクリプト")
    p.add_argument('ground_truth', help="正解 SVG のファイルパス")
    p.add_argument('llm_output',   help="LLM 出力 SVG のファイルパス")
    args = p.parse_args()

    try:
        _, gt_circs, _ = parse_svg_file(args.ground_truth, filter_class='additional_object')
        gt_segs, _, _ = parse_svg_file(args.ground_truth, filter_class='input_object')
        out_segs, out_circs, out_ells = parse_svg_file(args.llm_output, filter_class='output_object')
    except Exception:
        print("0")
        sys.exit(0)

    out_circs = filter_circles_intersecting_all_lines(gt_segs, out_circs)
           
    evaluation = match_circles(gt_circs, out_circs)

    print("1" if evaluation else "0")

if __name__ == '__main__':
    main()
