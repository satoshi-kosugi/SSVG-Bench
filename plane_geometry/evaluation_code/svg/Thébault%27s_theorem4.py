                      

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

def circle_iou(c1, r1, c2, r2):
                                                                 
    d = math.hypot(c1[0] - c2[0], c1[1] - c2[1])
           
    if d >= r1 + r2:
        return 0.0
                 
    if d <= abs(r1 - r2):
                                
        return (min(r1, r2) ** 2) / (max(r1, r2) ** 2)
               
    r1_sq = r1**2
    r2_sq = r2**2
    alpha = math.acos((d*d + r1_sq - r2_sq) / (2 * d * r1))
    beta  = math.acos((d*d + r2_sq - r1_sq) / (2 * d * r2))
    inter = (
        r1_sq * alpha +
        r2_sq * beta -
        0.5 * math.sqrt(
            (-d + r1 + r2) *
            ( d + r1 - r2) *
            ( d - r1 + r2) *
            ( d + r1 + r2)
        )
    )
    union = math.pi * (r1_sq + r2_sq) - inter
    return inter / union

def match_circles(gt_circs, out_circs, tol_center=1e1, tol_r=1e1):
\
\
\
\
\
       
    unmatched = list(out_circs)

    for (c_gt, r_gt) in gt_circs:
        if not unmatched:
            return False

        best_i = 0
        best_iou = circle_iou(c_gt, r_gt, unmatched[0][0], unmatched[0][1])
        for i, (c_out, r_out) in enumerate(unmatched[1:], start=1):
            iou = circle_iou(c_gt, r_gt, c_out, r_out)
            if iou > best_iou:
                best_iou = iou
                best_i    = i

        c_out, r_out = unmatched[best_i]
        dc = math.hypot(c_gt[0] - c_out[0], c_gt[1] - c_out[1])
        if dc <= tol_center and abs(r_gt - r_out) <= tol_r:
                         
            unmatched.pop(best_i)
        else:
            return False

    return True

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

def main():
    p = argparse.ArgumentParser(description="SVG 出力評価スクリプト")
    p.add_argument('ground_truth', help="正解 SVG のファイルパス")
    p.add_argument('llm_output',   help="LLM 出力 SVG のファイルパス")
    args = p.parse_args()

    try:
        gt_segs_red, _, _ = parse_svg_file(args.ground_truth, filter_class='output_object_red')
        gt_segs_blue, _, _ = parse_svg_file(args.ground_truth, filter_class='output_object_blue')
        gt_segs_aqua, _, _ = parse_svg_file(args.ground_truth, filter_class='output_object_aqua')
        gt_segs_lime, _, _ = parse_svg_file(args.ground_truth, filter_class='output_object_lime')
        out_segs, _, _ = parse_svg_file(args.llm_output, filter_class='output_object')
    except Exception:
        print("0")
        sys.exit(0)

    out_segs.extend(merge_collinear_segments(out_segs))

    stage_red = match_segments(gt_segs_red, out_segs)
    stage_blue = match_segments(gt_segs_blue, out_segs)
    stage_aqua = match_segments(gt_segs_aqua, out_segs)
    stage_lime = match_segments(gt_segs_lime, out_segs)

    print("1" if (stage_red or stage_blue or stage_aqua or stage_lime) else "0")

if __name__ == '__main__':
    main()
