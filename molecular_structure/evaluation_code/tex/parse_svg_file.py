                      

import math
import xml.etree.ElementTree as ET
import networkx as nx

def parse_svg_file(path, tol=1e-1):
    root  = ET.parse(path).getroot()

    G = nx.Graph()
             
    ns = {'svg': 'http://www.w3.org/2000/svg'}
    
    circles = []
                          
    for i, circle in enumerate(root.findall(".//svg:circle", ns)):
        cx = float(circle.attrib['cx'])
        cy = float(circle.attrib['cy'])
        fill = circle.attrib.get('fill', '')
        circles.append((cx, cy, fill, i))
        G.add_node(i, fill=fill, pos=(cx, cy))

    def find_circle(x, y):
        for cx, cy, fill, node_id in circles:
            if math.hypot(cx - x, cy - y) < tol:
                return node_id
        return None

    for line in root.findall(".//svg:line", ns):
        x1 = float(line.attrib['x1'])
        y1 = float(line.attrib['y1'])
        x2 = float(line.attrib['x2'])
        y2 = float(line.attrib['y2'])
        n1 = find_circle(x1, y1)
        n2 = find_circle(x2, y2)
                                   
        if n1 is not None and n2 is not None:
            G.add_edge(n1, n2)
    return G

