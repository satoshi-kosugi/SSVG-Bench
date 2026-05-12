                      

import argparse
import xml.etree.ElementTree as ET
import re
import math
import sys
import itertools
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

def segment_circle_intersections(a, b, c, r, tol=1e0):
\
\
\
       
    (x1,y1), (x2,y2) = a, b
    dx, dy = x2-x1, y2-y1
    fx, fy = x1-c[0], y1-c[1]
    A = dx*dx + dy*dy
    B = 2*(fx*dx + fy*dy)
    C = fx*fx + fy*fy - r*r
    disc = B*B - 4*A*C
    if disc < 0:
        return []
    ts = []
    sqrt_disc = math.sqrt(disc)
    for sign in (+1, -1):
        t = (-B + sign*sqrt_disc) / (2*A)
        if -tol <= t <= 1.0 + tol:
            ts.append(max(0.0, min(1.0, t)))
    pts = [(x1 + t*dx, y1 + t*dy) for t in set(ts)]
    return pts

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
    gt_sorted = sorted(gt_circs, key=lambda x: x[1])
    small_center, _ = gt_sorted[0]
    large_center, large_r = gt_sorted[-1]

    out_segs = merge_collinear_segments(out_segs)

    tol_seg = 1e1
    segs_through_small = [
        seg for seg in out_segs
        if dist_point_to_segment(small_center, seg[0], seg[1]) <= tol_seg
    ]

    crossing = [
        seg for seg in segs_through_small
        if len(segment_circle_intersections(seg[0], seg[1], large_center, large_r)) == 2
    ]
    if len(crossing) != 2:
        print("0"); sys.exit(0)

    raw_pts = list(itertools.chain.from_iterable(
        segment_circle_intersections(seg[0], seg[1], large_center, large_r)
        for seg in crossing
    ))
    unique_pts = []
    for p in raw_pts:
        if not any(math.hypot(p[0]-q[0], p[1]-q[1]) <= tol_seg for q in unique_pts):
            unique_pts.append(p)

    for (center, _) in out_circs:
        if not any(math.hypot(center[0]-p[0], center[1]-p[1]) <= tol_seg for p in unique_pts):
            print("0"); sys.exit(0)

    print("1")

if __name__ == '__main__':
    main()
