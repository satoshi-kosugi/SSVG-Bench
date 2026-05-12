                      

import argparse
import re
import math
import random
import sys
import os
import ast
import xml.etree.ElementTree as ET

def _dedup_pts(pts, eps=1e-6):
                        
    uniq = []
    for p in pts:
        if not any(abs(p[0]-q[0]) < eps and abs(p[1]-q[1]) < eps for q in uniq):
            uniq.append(p)
    return uniq

def _mat_mul(A, B):
    return [
        [A[0][0]*B[0][0] + A[0][1]*B[1][0] + A[0][2]*B[2][0],
         A[0][0]*B[0][1] + A[0][1]*B[1][1] + A[0][2]*B[2][1],
         A[0][0]*B[0][2] + A[0][1]*B[1][2] + A[0][2]*B[2][2]],
        [A[1][0]*B[0][0] + A[1][1]*B[1][0] + A[1][2]*B[2][0],
         A[1][0]*B[0][1] + A[1][1]*B[1][1] + A[1][2]*B[2][1],
         A[1][0]*B[0][2] + A[1][1]*B[1][2] + A[1][2]*B[2][2]],
        [0,0,1],
    ]

def _mat_apply(M, x, y):
    return (M[0][0]*x + M[0][1]*y + M[0][2],
            M[1][0]*x + M[1][1]*y + M[1][2])

def _mat_inv(M):
    a,c,e = M[0]
    b,d,f = M[1]
    det = a*d - b*c
    if abs(det) < 1e-12:
                       
        return [[1,0,0],[0,1,0],[0,0,1]]
    inv = [[ d/det, -c/det, 0],
           [-b/det,  a/det, 0],
           [     0,      0, 1]]
             
    tx = -(inv[0][0]*e + inv[0][1]*f)
    ty = -(inv[1][0]*e + inv[1][1]*f)
    inv[0][2] = tx
    inv[1][2] = ty
    return inv

def _mat_identity():
    return [[1,0,0],[0,1,0],[0,0,1]]

def _parse_transform_to_mat(txt):
\
\
       
    if not txt:
        return _mat_identity()
    t_re = re.compile(r'(matrix|translate|rotate|scale|skewX|skewY)\s*\(([^)]+)\)', re.I)

    def mat_translate(tx, ty=0.0): return [[1,0,tx],[0,1,ty],[0,0,1]]
    def mat_rotate(angle_deg, cx=0.0, cy=0.0):
        a = math.radians(angle_deg); c=math.cos(a); s=math.sin(a)
        R = [[c,-s,0],[s,c,0],[0,0,1]]
        return _mat_mul(_mat_mul(mat_translate(cx,cy), R), mat_translate(-cx,-cy))
    def mat_scale(sx, sy=None):
        if sy is None: sy = sx
        return [[sx,0,0],[0,sy,0],[0,0,1]]
    def mat_skewx(a_deg):
        t = math.tan(math.radians(a_deg)); return [[1,t,0],[0,1,0],[0,0,1]]
    def mat_skewy(a_deg):
        t = math.tan(math.radians(a_deg)); return [[1,0,0],[t,1,0],[0,0,1]]
    def mat_matrix(a,b,c,d,e,f): return [[a,c,e],[b,d,f],[0,0,1]]

    M = _mat_identity()
    for m in t_re.finditer(txt):
        name = m.group(1).lower()
        parts = [float(v) for v in re.split(r'[,\s]+', m.group(2).strip()) if v]
        if name == 'matrix' and len(parts)==6:
            Mi = mat_matrix(*parts)
        elif name == 'translate':
            Mi = mat_translate(parts[0], parts[1] if len(parts)>1 else 0.0)
        elif name == 'rotate':
            if len(parts) >= 3: Mi = mat_rotate(parts[0], parts[1], parts[2])
            else: Mi = mat_rotate(parts[0])
        elif name == 'scale':
            Mi = mat_scale(parts[0], parts[1] if len(parts)>1 else None)
        elif name == 'skewx': Mi = mat_skewx(parts[0])
        elif name == 'skewy': Mi = mat_skewy(parts[0])
        else: continue
        M = _mat_mul(M, Mi)
    return M

def _inverse_of_info_matrix(info_value):
\
\
\
       
    if not info_value:
        return _mat_identity()
    m = re.search(r'matrix\(\s*([-\d\.]+)\s*,\s*([-\d\.]+)\s*,\s*([-\d\.]+)\s*,\s*([-\d\.]+)\s*,\s*([-\d\.]+)\s*,\s*([-\d\.]+)\s*\)', info_value)
    if not m:
        return _mat_identity()
    a,b,c,d,e,f = map(float, m.groups())
    return _mat_inv([[a,c,e],[b,d,f],[0,0,1]])

def _composed_transform(elem_transform_str, inv_info_mat):
\
\
\
\
       
    Me = _parse_transform_to_mat(elem_transform_str or '')
    return _mat_mul(inv_info_mat, Me)

def _path_number_stream(d):
                                         
    return [float(x) for x in re.findall(r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?', d)]

def _extract_path_segments_endpoints(d):
\
\
\
\
\
\
\
       
    tokens = re.findall(r'[MLCZ]|[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?', d, flags=re.I)
    i = 0
    cur = None
    Mpt = None
    prev_t = ""
    L_pairs = []
    C_end = []
    while i < len(tokens):
        t = tokens[i]
        if t == 'M':
            x = float(tokens[i+1]); y = float(tokens[i+2])
            if i != 0 and tokens[i-1] in ('Z', 'z') and "L" in tokens:
                L_pairs.append((cur, (x,y)))
            cur = (x,y); Mpt = (x,y)
            i += 3
        elif t == 'L' and cur is not None:
            x = float(tokens[i+1]); y = float(tokens[i+2])
            L_pairs.append((cur, (x,y)))
            cur = (x,y)
            i += 3
        elif t == 'C' and cur is not None:

            i += 1
            while i+5 < len(tokens) and re.match(r'[-+0-9.]', tokens[i]):
                     
                x = float(tokens[i+4]); y = float(tokens[i+5])
                C_end.append((x,y))
                cur = (x,y)
                i += 6
        elif t in ('Z', 'z'):
            i += 1
        else:
                          
            i += 1

    return {'M': Mpt, 'L_pairs': L_pairs, 'C_endpoints': C_end}

def _collect_black_stroke_transforms(root):
\
\
\
\
\
       
    transforms = []
    for elem in root.iter():
                                                   
        if tag(elem) == 'svg':
            continue
        if elem.get('stroke') == 'rgb(0%, 0%, 0%)':
            transforms.append(elem.get('transform', '') or '')
    return transforms

def verify_black_stroke_transforms_equal(root, *, require_exist=False, raise_on_mismatch=False):
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
\
\
       
    transforms = _collect_black_stroke_transforms(root)
                   
    distinct = list(dict.fromkeys(transforms))
    counts = {}
    for t in transforms:
        counts[t] = counts.get(t, 0) + 1

    if not transforms:
        ok = (not require_exist)
        info = {
            "value": None,
            "distinct": distinct,
            "counts": counts,
            "total": 0,
        }
        if raise_on_mismatch and not ok:
            raise ValueError("stroke='rgb(0%, 0%, 0%)' の要素が1つもありません。")
        return ok, info

    ok = (len(distinct) == 1)
    info = {
        "value": distinct[0] if ok else None,
        "distinct": distinct,
        "counts": counts,
        "total": len(transforms),
    }

    if raise_on_mismatch and not ok:
        raise ValueError(
            f"transform が不一致です: distinct={distinct} counts={counts}"
        )
    return ok, info

def tag(elem):
                        
    return elem.tag.split('}')[-1]

def _find_parent(root, target):
                                         
    for parent in root.iter():
        for child in list(parent):
            if child is target:
                return parent
    return None

def _ungroup_all_g(root):
\
\
\

    while True:
        gs = [e for e in list(root.iter()) if tag(e) == 'g']
        if not gs:
            break
        for g in gs:
                          
            for child in list(g):

                root.append(child)
                        
            parent = _find_parent(root, g)
            if parent is not None:
                parent.remove(g)

def _keep_only_black_fill_or_stroke_attr(root, remove_dash=False):
\
\
\
       
    def is_ok(e):
        if remove_dash and e.get("stroke-dasharray") is not None:
            return False
        f = e.get('fill')
        s = e.get('stroke')
        return ((f is not None) and 'rgb' in f) or ((s is not None) and 'rgb' in s)

    for child in list(root):
                                     
        if not is_ok(child):
            root.remove(child)

    for e in list(root.iter()):
        if e is root:
            continue
                                              
        parent = _find_parent(root, e)
        if parent is not None and parent is not root:
            if not is_ok(e):
                parent.remove(e)

_RGB_FUNC_RE = re.compile(
    r'rgb\(\s*([+-]?\d*\.?\d+)\s*(%)?\s*,\s*([+-]?\d*\.?\d+)\s*(%)?\s*,\s*([+-]?\d*\.?\d+)\s*(%)?\s*\)',
    re.IGNORECASE
)

def _clamp(v, lo, hi):
    return max(lo, min(hi, v))

def _normalize_rgb_to_percent(rgb):
\
\
\
\
\
       
    r, g, b = rgb
    if any(v > 100 for v in (r, g, b)):
        r = round(_clamp(r, 0, 255) / 255.0 * 100)
        g = round(_clamp(g, 0, 255) / 255.0 * 100)
        b = round(_clamp(b, 0, 255) / 255.0 * 100)
    else:
        r = round(_clamp(r, 0, 100))
        g = round(_clamp(g, 0, 100))
        b = round(_clamp(b, 0, 100))
    return (int(r), int(g), int(b))

def _parse_rgb_function(value):
\
\
\
       
    if not value or not isinstance(value, str):
        return None
    m = _RGB_FUNC_RE.search(value)
    if not m:
        return None
    vals = []
    for i in (1, 3, 5):
        num = float(m.group(i))
        is_percent = bool(m.group(i + 1))
        if is_percent:
            vals.append(num)         
        else:
            vals.append(num)                  
    return _normalize_rgb_to_percent(tuple(vals))

def _parse_style_attr(style_str):
\
\
       
    props = {}
    if not style_str:
        return props
    for chunk in style_str.split(';'):
        if ':' in chunk:
            k, v = chunk.split(':', 1)
            props[k.strip().lower()] = v.strip()
    return props

def _extract_candidate_colors(elem):
\
\
\
\
\
       
    colors = []
          
    for attr in ('fill', 'stroke'):
        val = elem.get(attr)
        if val and val.lower() != 'none':
            c = _parse_rgb_function(val)
            if c is not None:
                colors.append(c)
              
    style = elem.get('style')
    if style:
        props = _parse_style_attr(style)
        for attr in ('fill', 'stroke'):
            val = props.get(attr)
            if val and val.lower() != 'none':
                c = _parse_rgb_function(val)
                if c is not None:
                    colors.append(c)
    return colors

def _ok_color(elem, filter_color):
\
\
\
       
    if filter_color is None:
        return True
    target = _normalize_rgb_to_percent(tuple(filter_color))
    for c in _extract_candidate_colors(elem):
        if c == target:
            return True
    return False

def parse_segments(root, filter_color=None, info_value=None):
\
\
\
\
       
    segs = []
    inv_info = _inverse_of_info_matrix(info_value)

    for elem in root.iter():
        if tag(elem) != 'path':
            continue
        if not _ok_color(elem, filter_color):
            continue

        d = (elem.get('d') or '').strip()
        if not d:
            continue

        parts = _extract_path_segments_endpoints(d)
        if not parts['L_pairs']:
            continue

        M_total = _composed_transform(elem.get('transform'), inv_info)

        for (p0, p1) in parts['L_pairs']:
            a = _mat_apply(M_total, *p0)
            b = _mat_apply(M_total, *p1)
            segs.append((a, b))

    return segs

def parse_circles(root, filter_color=None, info_value=None):
\
\
\
\
\
\
       
    circs = []
    inv_info = _inverse_of_info_matrix(info_value)

    for elem in root.iter():
        if tag(elem) != 'path':
            continue
        if not _ok_color(elem, filter_color):
            continue

        d = (elem.get('d') or '').strip()
        if not d:
            continue

        parts = _extract_path_segments_endpoints(d)
        if parts['M'] is None or not parts['C_endpoints']:
            continue

        pts = [parts['M']] + parts['C_endpoints']

        if len(pts) >= 2 and abs(pts[0][0]-pts[-1][0]) < 1e-9 and abs(pts[0][1]-pts[-1][1]) < 1e-9:
            pts = pts[:-1]

        if len(pts) < 3:
            continue

        M_total = _composed_transform(elem.get('transform'), inv_info)
        tpts = [_mat_apply(M_total, x, y) for (x,y) in pts]

        cx = sum(p[0] for p in tpts) / len(tpts)
        cy = sum(p[1] for p in tpts) / len(tpts)
        r  = sum(math.hypot(p[0]-cx, p[1]-cy) for p in tpts) / len(tpts)

        circs.append(((cx, cy), r))

    return circs

def parse_ellipses(root, filter_color=None, info_value=None):
\
\
\
\
\
\
\
\
\
       
    ells = []
    inv_info = _inverse_of_info_matrix(info_value)

    for elem in root.iter():
        if tag(elem) != 'path':
            continue
        if not _ok_color(elem, filter_color):
            continue

        d = (elem.get('d') or '').strip()
        if not d:
            continue

        parts = _extract_path_segments_endpoints(d)
        if parts['M'] is None or not parts['C_endpoints']:
            continue

        pts = [parts['M']] + parts['C_endpoints']
                  
        if len(pts) >= 2 and abs(pts[0][0]-pts[-1][0]) < 1e-9 and abs(pts[0][1]-pts[-1][1]) < 1e-9:
            pts = pts[:-1]

        M_total = _composed_transform(elem.get('transform'), inv_info)
        tpts = [_mat_apply(M_total, x, y) for (x, y) in pts]
        tpts = _dedup_pts(tpts)

        if len(tpts) < 3:
            continue

        cx = sum(p[0] for p in tpts) / len(tpts)
        cy = sum(p[1] for p in tpts) / len(tpts)

        vecs = [ (p[0]-cx, p[1]-cy) for p in tpts ]

        radii_ = [ math.hypot(vx, vy) for (vx, vy) in vecs ]
                 
        if not radii_:
            continue
        R_major = max(radii_)
        R_minor = min(radii_)
        if R_minor / R_major > 0.95:
            continue
        
        if len(vecs) < 3:
            continue

        Sxx = sum(vx*vx for vx,vy in vecs)
        Syy = sum(vy*vy for vx,vy in vecs)
        Sxy = sum(vx*vy for vx,vy in vecs)

        if Sxx + Syy < 1e-15:
                        
            continue

        theta = 0.5 * math.atan2(2.0*Sxy, (Sxx - Syy))
        c = math.cos(theta)
        s = math.sin(theta)

        ab = []
        for vx, vy in vecs:
            a =  vx*c + vy*s
            b = -vx*s + vy*c
            ab.append((a, b))

        A11 = sum(a*a*a*a for a,b in ab)                   
        A12 = sum((a*a)*(b*b) for a,b in ab)                   
        A22 = sum(b*b*b*b for a,b in ab)                   
        v1  = sum(a*a for a,b in ab)                       
        v2  = sum(b*b for a,b in ab)                       

        det = A11*A22 - A12*A12
        if abs(det) < 1e-18:
                                             
            radii = [ math.hypot(vx, vy) for vx,vy in vecs ]
            if not radii:
                continue
            rx = max(radii)
            ry = max(min(radii), 1e-12)
            angle_deg = math.degrees(theta)
            ells.append(((cx, cy), rx, ry, angle_deg))
            continue

        alpha = ( v1*A22 - v2*A12) / det
        beta  = (-v1*A12 + v2*A11) / det

        eps = 1e-18
        alpha = max(alpha, eps)
        beta  = max(beta,  eps)

        rx = (1.0 / math.sqrt(alpha))
        ry = (1.0 / math.sqrt(beta))

        if ry > rx:
            rx, ry = ry, rx
                                     
            theta += math.pi * 0.5
                              
        angle_deg = math.degrees(theta)

        if ry / max(rx, 1e-12) > 0.9999:
                                     
            angle_deg = 0.0

        ells.append(((cx, cy), rx, ry, angle_deg))

    return ells

def parse_svg_file(path, filter_class=None):
                 
    root  = ET.parse(path).getroot()

    _ungroup_all_g(root)
    _keep_only_black_fill_or_stroke_attr(root, remove_dash=(("GT" in path) and ("Griffiths" not in path)))

    ok, info = verify_black_stroke_transforms_equal(root, require_exist=False)
                                                           
    info_value = info.get("value")

    if filter_class == 'output_object' or filter_class == 'output_object_red':
        filter_color = [100, 0, 0]
    elif filter_class == 'input_object':
        filter_color = [0, 0, 0]
    elif filter_class == 'output_object_blue':
        filter_color = [0, 0, 100]
    elif filter_class == 'output_object_green':
        filter_color = [0, 100, 0]
    elif filter_class == 'output_object_aqua':
        filter_color = [0, 67.83905, 93.728638]
    elif filter_class == 'output_object_lime':
        filter_color = [75, 100, 0]
    else:
        filter_color = None

    segs  = parse_segments(root, filter_color, info_value)
    circs = parse_circles(root, filter_color, info_value)
    ells  = parse_ellipses(root, filter_color, info_value)

    return segs, circs, ells