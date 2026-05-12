                      

import argparse
import re
import math
import random
import sys
import os
import ast
import xml.etree.ElementTree as ET

def tag(elem):
                        
    return elem.tag.split('}')[-1]

def parse_segments(root, filter_class=None):
    segs = []
    def ok_class(elem):
        if filter_class is None:
            return True
        return filter_class in elem.get('class','').split()

    for elem in root.iter():
        t = tag(elem)

        def safe_float(value):
            try:
                return float(value)
            except (TypeError, ValueError):
                return 0.0
        if t == 'line' and ok_class(elem):
            x1 = safe_float(elem.get('x1', 0))
            y1 = safe_float(elem.get('y1', 0))
            x2 = safe_float(elem.get('x2', 0))
            y2 = safe_float(elem.get('y2', 0))
            segs.append(((x1, y1), (x2, y2)))

        elif t == 'polygon' and ok_class(elem):
            pts = re.split(r'[,\s]+', elem.get('points','').strip())
            coords = [float(v) for v in pts if v]
            pts_list = list(zip(coords[0::2], coords[1::2]))
            for i in range(len(pts_list)):
                segs.append((pts_list[i], pts_list[(i+1) % len(pts_list)]))

        elif t == 'polyline' and ok_class(elem):
            pts = re.split(r'[,\s]+', elem.get('points','').strip())
            coords = [float(v) for v in pts if v]
            pts_list = list(zip(coords[0::2], coords[1::2]))
            for i in range(len(pts_list)-1):
                segs.append((pts_list[i], pts_list[i+1]))

        elif t == 'path' and ok_class(elem):
            d = elem.get('d','')
            tokens = re.findall(r'[ML]|[-+]?\d*\.?\d+(?:\.\d+)?', d)
            cur = None
            i = 0
            while i < len(tokens):
                tok = tokens[i]
                if tok == 'M':
                    cur = (float(tokens[i+1]), float(tokens[i+2]))
                    i += 3
                elif tok == 'L' and cur is not None:
                    nxt = (float(tokens[i+1]), float(tokens[i+2]))
                    segs.append((cur, nxt))
                    cur = nxt
                    i += 3
                else:
                    i += 1

        elif t == 'rect' and ok_class(elem):
            x = float(elem.get('x', '0'))
            y = float(elem.get('y', '0'))
            w = float(elem.get('width', '0'))
            h = float(elem.get('height', '0'))
            p1 = (x, y)
            p2 = (x + w, y)
            p3 = (x + w, y + h)
            p4 = (x, y + h)
            segs.extend([(p1, p2), (p2, p3), (p3, p4), (p4, p1)])

    return segs

def parse_circles(root, filter_class=None):
\
\
\
       
    circs = []
    for elem in root.iter():
        if tag(elem) == 'circle':
            cls = elem.get('class','').split()
            if filter_class is None or filter_class in cls:
                cx = float(elem.get('cx', 0))
                cy = float(elem.get('cy', 0))
                r  = float(elem.get('r', 0))
                circs.append(((cx, cy), r))
    return circs

import re, math

def parse_ellipses(root, filter_class=None):
       
    ellipses = []
                       
    t_re = re.compile(r'(matrix|translate|rotate|scale|skewX|skewY)\s*\(([^)]+)\)', re.I)

    def mult(A, B):
                           
        return [
            [A[0][0]*B[0][0] + A[0][1]*B[1][0] + A[0][2]*B[2][0],
             A[0][0]*B[0][1] + A[0][1]*B[1][1] + A[0][2]*B[2][1],
             A[0][0]*B[0][2] + A[0][1]*B[1][2] + A[0][2]*B[2][2]],
            [A[1][0]*B[0][0] + A[1][1]*B[1][0] + A[1][2]*B[2][0],
             A[1][0]*B[0][1] + A[1][1]*B[1][1] + A[1][2]*B[2][1],
             A[1][0]*B[0][2] + A[1][1]*B[1][2] + A[1][2]*B[2][2]],
            [0, 0, 1],
        ]

    def mat_translate(tx, ty=0.0):
        return [[1,0,tx],[0,1,ty],[0,0,1]]

    def mat_rotate(angle_deg, cx=0.0, cy=0.0):
        a = math.radians(angle_deg)
        c = math.cos(a); s = math.sin(a)
                              
        return mult(mult(mat_translate(cx, cy), [[c,-s,0],[s,c,0],[0,0,1]]), mat_translate(-cx, -cy))

    def mat_scale(sx, sy=None):
        if sy is None: sy = sx
        return [[sx,0,0],[0,sy,0],[0,0,1]]

    def mat_skewx(a_deg):
        t = math.tan(math.radians(a_deg))
        return [[1,math.tan(0),0],[t,1,0],[0,0,1]]                                        
    def mat_skewy(a_deg):
        t = math.tan(math.radians(a_deg))
        return [[1,t,0],[math.tan(0),1,0],[0,0,1]]                                        

    def mat_matrix(a,b,c,d,e,f):
                                                        
        return [[a,c,e],[b,d,f],[0,0,1]]

    def parse_transform(txt):
                                                  
        M = [[1,0,0],[0,1,0],[0,0,1]]
        for m in t_re.finditer(txt or ''):
            name = m.group(1).lower()
            parts = [float(v) for v in re.split(r'[,\s]+', m.group(2).strip()) if v]
            if name == 'matrix' and len(parts) == 6:
                Mi = mat_matrix(*parts)
            elif name == 'translate':
                Mi = mat_translate(parts[0], parts[1] if len(parts) > 1 else 0.0)
            elif name == 'rotate':
                if len(parts) >= 3:
                    Mi = mat_rotate(parts[0], parts[1], parts[2])
                else:
                    Mi = mat_rotate(parts[0])
            elif name == 'scale':
                Mi = mat_scale(parts[0], parts[1] if len(parts) > 1 else None)
            elif name == 'skewx':
                Mi = mat_skewx(parts[0])
            elif name == 'skewy':
                Mi = mat_skewy(parts[0])
            else:
                continue
            M = mult(M, Mi)
        return M

    def apply_affine(M, x, y):
                                  
        return (M[0][0]*x + M[0][1]*y + M[0][2],
                M[1][0]*x + M[1][1]*y + M[1][2])

    def decompose_axes(Mlin, rx, ry):
           
        a, c = Mlin[0][0], Mlin[0][1]
        b, d = Mlin[1][0], Mlin[1][1]

        arx, cry = a*rx, c*ry
        brx, dry = b*rx, d*ry
                                     
        p = arx*arx + cry*cry
        q = brx*brx + dry*dry
        r = arx*brx + cry*dry
                  
        trace = p + q
        diff  = p - q
        disc  = math.hypot(diff, 2*r)                         
        lam1 = 0.5*(trace + disc)        
        lam2 = 0.5*(trace - disc)        
                 
        R1 = math.sqrt(max(lam1, 0.0))
        R2 = math.sqrt(max(lam2, 0.0))
                                          
        angle = 0.5 * math.atan2(2*r, diff) if (abs(r) + abs(diff)) > 0 else 0.0
        return R1, R2, math.degrees(angle)

    for elem in root.iter():
        if tag(elem) == 'ellipse':
            cls = elem.get('class','').split()
            if filter_class is not None and filter_class not in cls:
                continue
            cx = float(elem.get('cx', 0.0))
            cy = float(elem.get('cy', 0.0))
            rx = float(elem.get('rx', 0.0))
            ry = float(elem.get('ry', 0.0))

            M = parse_transform(elem.get('transform',''))

            cx_t, cy_t = apply_affine(M, cx, cy)

            Mlin = [[M[0][0], M[0][1]],
                    [M[1][0], M[1][1]]]

            if rx == 0.0 and ry == 0.0:
                R1 = R2 = 0.0
                angle_deg = 0.0
            else:
                R1, R2, angle_deg = decompose_axes(Mlin, rx, ry)

            ellipses.append(((cx_t, cy_t), R1, R2, angle_deg))

        elif tag(elem) == 'circle' and elem.get('transform','') != '':
            cls = elem.get('class','').split()
            if filter_class is not None and filter_class not in cls:
                continue
            cx = float(elem.get('cx', 0.0))
            cy = float(elem.get('cy', 0.0))
            rx = float(elem.get('r', 0.0))
            ry = float(elem.get('r', 0.0))

            M = parse_transform(elem.get('transform',''))

            cx_t, cy_t = apply_affine(M, cx, cy)

            Mlin = [[M[0][0], M[0][1]],
                    [M[1][0], M[1][1]]]

            if rx == 0.0 and ry == 0.0:
                R1 = R2 = 0.0
                angle_deg = 0.0
            else:
                R1, R2, angle_deg = decompose_axes(Mlin, rx, ry)

            ellipses.append(((cx_t, cy_t), R1, R2, angle_deg))
    return ellipses

def parse_svg_file(path, filter_class=None):
    root  = ET.parse(path).getroot()
    segs = parse_segments(root, filter_class)
    circs = parse_circles(root, filter_class)
    ells = parse_ellipses(root, filter_class)
    return segs, circs, ells