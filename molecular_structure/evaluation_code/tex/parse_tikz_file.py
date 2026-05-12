                      

import re
import math
import os
import ast
import networkx as nx
import xml.etree.ElementTree as ET

def parse_tikz_file(path, tol=1e-1):
       
    tree = ET.parse(path)
    root = tree.getroot()
    ns = {'svg': 'http://www.w3.org/2000/svg'}
    G = nx.Graph()

    circles = []                               
    node_id = 0

    for circ in root.findall(".//svg:circle", ns):
        cx = float(circ.get('cx'))
        cy = float(circ.get('cy'))
        fill = circ.get('fill', '')
        circles.append((cx, cy, fill, node_id))
        G.add_node(node_id, fill=fill, pos=(cx, cy))
        node_id += 1

    for p in root.findall(".//svg:path", ns):
                                            
        if 'clip-rule' in p.attrib:
            continue
        fill = p.get('fill', '')
        d    = p.get('d', '')
                                  
        if not d or fill == 'none':
            continue
                         
        if 'fill-rule' in p.attrib and 'C' in d:
                                       
            nums   = list(map(float, re.findall(r'[-+]?[0-9]*\.?[0-9]+', d)))
            coords = [(nums[i], nums[i+1]) for i in range(0, len(nums), 2)]
            xs = [x for x,y in coords]
            ys = [y for x,y in coords]
            cx = (min(xs)+max(xs)) / 2
            cy = (min(ys)+max(ys)) / 2

            tr = p.get('transform','')
            if tr.startswith('matrix'):
                a,b,c,d_mat,e,f = map(
                    float, re.findall(r'[-+]?[0-9]*\.?[0-9]+', tr)
                )
                cx, cy = a*cx + c*cy + e, b*cx + d_mat*cy + f

            if fill.startswith('rgb'):
                ps = re.findall(r'(\d+\.?\d*)%', fill)
                rgb = tuple(int(round(float(p)/100*255)) for p in ps)
                fill_hex = '#{:02X}{:02X}{:02X}'.format(*rgb)

            circles.append((cx, cy, fill_hex, node_id))
            G.add_node(node_id, fill=fill_hex, pos=(cx, cy))
            node_id += 1

    def find_circle(x, y):
        for cx, cy, fill, nid in circles:
            if math.hypot(cx - x, cy - y) < tol:
                return nid
        return None

    for p in root.findall(".//svg:path", ns):
        if 'clip-rule' in p.attrib:
            continue
        if p.get('fill') != 'none':
            continue
        d = p.get('d', '')
                               
        m = re.match(
            r'\s*M\s*([-+]?[0-9]*\.?[0-9]+)\s*'
            r'([-+]?[0-9]*\.?[0-9]+)\s*L\s*'
            r'([-+]?[0-9]*\.?[0-9]+)\s*'
            r'([-+]?[0-9]*\.?[0-9]+)',
            d
        )
        if not m:
            continue
        x1, y1, x2, y2 = map(float, m.groups())

        tr = p.get('transform','')
        if tr.startswith('matrix'):
            a, b, c, d_mat, e, f = map(
                float, re.findall(r'[-+]?[0-9]*\.?[0-9]+', tr)
            )
            x1, y1 = a*x1 + c*y1 + e, b*x1 + d_mat*y1 + f
            x2, y2 = a*x2 + c*y2 + e, b*x2 + d_mat*y2 + f

        n1 = find_circle(x1, y1)
        n2 = find_circle(x2, y2)
        if n1 is not None and n2 is not None:
            G.add_edge(n1, n2)

    return G