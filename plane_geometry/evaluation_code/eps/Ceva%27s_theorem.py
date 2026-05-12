                      

import argparse
import xml.etree.ElementTree as ET
import re
import math
import sys
import itertools
from parse_svg_file import parse_svg_file

def dist_point_to_segment(pt, a, b):
    x,y = pt; x1,y1 = a; x2,y2 = b
    dx,dy = x2-x1, y2-y1
    if dx==0 and dy==0:
        return math.hypot(x-x1, y-y1)
    t = ((x-x1)*dx + (y-y1)*dy)/(dx*dx+dy*dy)
    t = max(0.0, min(1.0, t))
    proj = (x1+t*dx, y1+t*dy)
    return math.hypot(x-proj[0], y-proj[1])

def line_intersection(p1, d1, p2, d2, tol=1e-9):
    cross = d1[0]*d2[1] - d1[1]*d2[0]
    if abs(cross)<tol:
        return None
    t1 = ((p2[0]-p1[0])*d2[1] - (p2[1]-p1[1])*d2[0]) / cross
    return (p1[0]+t1*d1[0], p1[1]+t1*d1[1])

def point_in_triangle(p, tri, tol=1e-9):
    (x,y), (x1,y1), (x2,y2), (x3,y3) = (p, *tri)
                        
    denom = (y2 - y3)*(x1 - x3) + (x3 - x2)*(y1 - y3)
    if abs(denom) < tol:
        return False
    w1 = ((y2 - y3)*(x - x3) + (x3 - x2)*(y - y3)) / denom
    w2 = ((y3 - y1)*(x - x3) + (x1 - x3)*(y - y3)) / denom
    w3 = 1 - w1 - w2
    return (w1 >= -tol) and (w2 >= -tol) and (w3 >= -tol)

import math

def merge_collinear_segments(segments, angle_tol=math.radians(5)):
\
\
       
    n = len(segments)
    used = [False] * n                    
    merged_new = []                          

    thresh = -math.cos(angle_tol)

    for i in range(n):
        if used[i]:
            continue
        u, v = segments[i]
        for j in range(i + 1, n):
            if used[j]:
                continue
            w, x = segments[j]

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

            vec1 = (p1[0] - shared[0], p1[1] - shared[1])
            vec2 = (p2[0] - shared[0], p2[1] - shared[1])
            n1, n2 = math.hypot(*vec1), math.hypot(*vec2)
            if n1 == 0 or n2 == 0:
                continue

            cosang = (vec1[0]*vec2[0] + vec1[1]*vec2[1]) / (n1 * n2)
            if cosang <= thresh:
                                                       
                used[i] = True
                used[j] = True
                merged_new.append((p1, p2))
                break                         

    result = [segments[k] for k in range(n) if not used[k]]
    result.extend(merged_new)
    return result

if __name__ == '__main__':
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

    out_segs = merge_collinear_segments(out_segs)

    vertices = set()
    for a,b in gt_segs:
        vertices.add(a)
        vertices.add(b)
    if len(vertices) != 3:
                                              
        print(0)
        sys.exit(0)
    triangle = list(vertices)                               

    tol = 1e1
    for v in triangle:
        ok = any(dist_point_to_segment(v, seg_a, seg_b) < tol
                for seg_a,seg_b in out_segs)
        if not ok:
            print(0)
            sys.exit(0)

    for v in triangle:
                                         
        opp_seg = next(seg for seg in gt_segs if seg[0] != v and seg[1] != v)

        ok = False
        for a,b in out_segs:
            if dist_point_to_segment(v, a, b) < tol:
                                         
                d_ab = (b[0]-a[0], b[1]-a[1])
                d_opp = (opp_seg[1][0]-opp_seg[0][0], opp_seg[1][1]-opp_seg[0][1])
                ip = line_intersection(a, d_ab, opp_seg[0], d_opp, tol=tol)
                               
                if ip is not None\
                and dist_point_to_segment(ip, a, b) < tol\
                and dist_point_to_segment(ip, opp_seg[0], opp_seg[1]) < tol:
                    ok = True
                    break
        if not ok:
            print(0)
            sys.exit(0)

    inter_pts = []
    for i, (p1,p2) in enumerate(out_segs):
        d1 = (p2[0]-p1[0], p2[1]-p1[1])
        for q1,q2 in out_segs[i+1:]:
            d2 = (q2[0]-q1[0], q2[1]-q1[1])
            ip = line_intersection(p1, d1, q1, d2, tol=tol)
            if ip is None:
                continue
                                                          
            if (dist_point_to_segment(ip, p1, p2) < tol and
                dist_point_to_segment(ip, q1, q2) < tol):
                inter_pts.append(ip)

    if not inter_pts:
        print(0)
        sys.exit(0)

    unique_pts = []
    for (x,y) in inter_pts:
        if not any(math.hypot(x-ux, y-uy) < tol for ux,uy in unique_pts):
            unique_pts.append((x,y))

    if len(unique_pts) != 1:
                                                            
        print(0)
        sys.exit(0)

    incenter = unique_pts[0]

    if point_in_triangle(incenter, triangle, tol=tol):
        print(1)
    else:
        print(0)
