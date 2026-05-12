                      

import argparse
import xml.etree.ElementTree as ET
import re
import math
import sys
from parse_svg_file import parse_svg_file

tol_center = 1e-1                                                                
tol_r      = 1e-1                                  
tol_line   = 1e-1                                                                        

def dist_point_to_segment(pt, a, b):
\
\
       
    x,y = pt
    x1,y1 = a
    x2,y2 = b
    dx = x2 - x1
    dy = y2 - y1
    if dx==0 and dy==0:
        return math.hypot(x-x1, y-y1)
    t = ((x-x1)*dx + (y-y1)*dy) / (dx*dx + dy*dy)
    t = max(0.0, min(1.0, t))
    proj_x = x1 + t*dx
    proj_y = y1 + t*dy
    return math.hypot(x - proj_x, y - proj_y)

def circle_intersections(c1, r1, c2, r2, tol=1e-6):
\
\
\
\
\
       
    x0,y0 = c1
    x1,y1 = c2
    dx = x1 - x0
    dy = y1 - y0
    d = math.hypot(dx,dy)
                                  
    if d < tol or d > r1 + r2 + tol or d < abs(r1 - r2) - tol:
        return []
                                             
    a = (r1*r1 - r2*r2 + d*d) / (2*d)
    h2 = r1*r1 - a*a
    if h2 < 0 and abs(h2) <= tol:
        h = 0.0
    elif h2 < 0:
        return []
    else:
        h = math.sqrt(h2)
    xm = x0 + a * dx / d
    ym = y0 + a * dy / d
    rx = -dy * (h / d)
    ry = dx * (h / d)
    p1 = (xm + rx, ym + ry)
    p2 = (xm - rx, ym - ry)
    return [p1] if h == 0 else [p1, p2]

def main():
    p = argparse.ArgumentParser(description="SVG Output Evaluation Script")
    p.add_argument('ground_truth', help="File path of correct SVG")
    p.add_argument('llm_output',   help="File path of SVG output from LLM")
    args = p.parse_args()

    try:
        gt_segs, gt_circs, gt_ells = parse_svg_file(args.ground_truth, filter_class='input_object')
        out_segs, out_circs, out_ells = parse_svg_file(args.llm_output, filter_class='output_object')
    except Exception:
        print("0")
        sys.exit(0)

    input_line = gt_segs[0]
    if input_line is None:
        print("0"); sys.exit(0)

    p1, p2 = input_line

    c1 = r1 = c2 = r2 = None

    for center, r in out_circs:
        if math.hypot(center[0]-p1[0], center[1]-p1[1]) <= tol_center:
            c1, r1 = center, r
            break
    if c1 is None:
        print("0"); sys.exit(0)

    for center, r in out_circs:
                                                                       
        if (abs(center[0]-c1[0]) > tol_center or abs(center[1]-c1[1]) > tol_center)\
           and math.hypot(center[0]-p2[0], center[1]-p2[1]) <= tol_center:
            c2, r2 = center, r
            break
    if c2 is None:
        print("0"); sys.exit(0)

    line_len = math.hypot(p2[0]-p1[0], p2[1]-p1[1])
    if abs(r1 - r2) > tol_r or r1 <= line_len/2 - tol_r:
        print("0"); sys.exit(0)

    inters = circle_intersections(c1, r1, c2, r2, tol=tol_r)
    if len(inters) < 2:
        print("0"); sys.exit(0)

    found_line = False
    for q1, q2 in out_segs:
        if dist_point_to_segment(inters[0], q1, q2) <= tol_line\
           and dist_point_to_segment(inters[1], q1, q2) <= tol_line:
            found_line = True
            break

    if not found_line:
        print("0"); sys.exit(0)

    print("1")

if __name__ == '__main__':
    main()
