                      

import argparse
import xml.etree.ElementTree as ET
import re
import math
import sys
from parse_svg_file import parse_svg_file

def merge_collinear_segments(segments, angle_tol=math.radians(5), dist_tol= 1):
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\
\

    segs = []
    for (p, q) in segments:
        if p == q:
            continue
        segs.append((p, q))
    if not segs:
        return []

    cos_ang_thr = math.cos(angle_tol)

    def unit(vx, vy):
        n = math.hypot(vx, vy)
        return (vx / n, vy / n)

    def canonical_dir(dx, dy):
                                   
        ux, uy = unit(dx, dy)
                            
        if ux < 0 or (abs(ux) <= 1e-15 and uy < 0):
            ux, uy = -ux, -uy
        return (ux, uy)

    clusters = []                                                     

    for (p, q) in segs:
        dx, dy = q[0] - p[0], q[1] - p[1]
        ux, uy = canonical_dir(dx, dy)
        nx, ny = -uy, ux                            
        r = nx * p[0] + ny * p[1]                         

        assigned = False
        for cl in clusters:
                              
            dot = cl["u"][0] * ux + cl["u"][1] * uy        
            if dot < cos_ang_thr:
                continue

            r_seg = cl["n"][0] * p[0] + cl["n"][1] * p[1]
            if abs(r_seg - cl["r"]) > dist_tol:
                continue

            cl["segs"].append((p, q))
            assigned = True
            break

        if not assigned:
            clusters.append({
                "u": (ux, uy),
                "n": (nx, ny),
                "r": r,
                "segs": [(p, q)],
            })

    merged = []
    for cl in clusters:
        ux, uy = cl["u"]
        nx, ny = cl["n"]
        r = cl["r"]

        intervals = []
        for (p, q) in cl["segs"]:
            t1 = ux * p[0] + uy * p[1]
            t2 = ux * q[0] + uy * q[1]
            a, b = (t1, t2) if t1 <= t2 else (t2, t1)
            intervals.append([a, b])

        intervals.sort(key=lambda ab: ab[0])
        merged_intervals = []
        for ab in intervals:
            if not merged_intervals:
                merged_intervals.append(ab)
            else:
                cur = merged_intervals[-1]
                if ab[0] <= cur[1] + dist_tol:            
                    cur[1] = max(cur[1], ab[1])
                else:
                    merged_intervals.append(ab)

        for a, b in merged_intervals:
            p = (ux * a + nx * r, uy * a + ny * r)
            q = (ux * b + nx * r, uy * b + ny * r)
            merged.append((p, q))

    return merged

def line_segment_passes_through_point(a, b, pt, tol=1e0):
                                                 
    x,y = pt; x1,y1 = a; x2,y2 = b
    dx, dy = x2-x1, y2-y1
    if dx==0 and dy==0:
        return math.hypot(x-x1, y-y1) <= tol
    t = ((x-x1)*dx + (y-y1)*dy)/(dx*dx + dy*dy)
    if t < -0.1 or t > 1.1:
        return False
    proj = (x1 + t*dx, y1 + t*dy)
    return math.hypot(x-proj[0], y-proj[1]) <= tol

def intersect_segment_circle(a, b, center, radius, tol=1e-3):
\
\
\
       
    x1,y1 = a; x2,y2 = b; cx,cy = center
    dx, dy = x2-x1, y2-y1
    A = dx*dx + dy*dy
    B = 2*(dx*(x1-cx) + dy*(y1-cy))
    C = (x1-cx)**2 + (y1-cy)**2 - radius*radius
    disc = (B*B - 4*A*C)
    if (disc / ((2 * A) ** 2)) < -tol:
        return []
    if abs(disc / ((2 * A) ** 2)) <= tol:
        t = -B/(2*A)
        return [(x1+dx*t, y1+dy*t)] if -0.1<=t<=1.1 else []
    sqrt_d = math.sqrt(disc)
    ts = [(-B+sqrt_d)/(2*A), (-B-sqrt_d)/(2*A)]
    pts = []
    for t in ts:
                                      
        if -0.1 <= t <= 1.1:
            pts.append((x1+dx*t, y1+dy*t))
    return pts

def dist_point_to_segment(pt, a, b):
                          
    x, y = pt; x1, y1 = a; x2, y2 = b
    dx, dy = x2-x1, y2-y1
    if dx == 0 and dy == 0:
        return math.hypot(x-x1, y-y1)
    t = ((x-x1)*dx + (y-y1)*dy) / (dx*dx + dy*dy)
    t = max(0.0, min(1.0, t))
    proj = (x1 + t*dx, y1 + t*dy)
    return math.hypot(x-proj[0], y-proj[1])

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

    if len(gt_circs) < 2:
        print("0"); sys.exit(0)
                        
    gt_circs.sort(key=lambda x: x[1])
    (c_small, r_small), (c_large, r_large) = gt_circs[0], gt_circs[-1]

    out_segs = merge_collinear_segments(out_segs)

    tol_center = 5e0
    segs_through = [
        seg for seg in out_segs
        if line_segment_passes_through_point(seg[0], seg[1], c_small, tol_center)
    ]
    if len(segs_through) != 2:
        print("0"); sys.exit(0)

    inter_counts = [len(intersect_segment_circle(a,b,c_large,r_large))
                    for a,b in segs_through]
    if sorted(inter_counts) != [1,2]:
        print("0"); sys.exit(0)

    if not any(abs(dist_point_to_segment(c_large, a, b) - r_large) < tol_center for a,b in segs_through):
        print("0"); sys.exit(0)

    inter_points = []
    for a,b in segs_through:
        inter_points += intersect_segment_circle(a, b, c_large, r_large)

    print("1")

if __name__ == '__main__':
    main()
