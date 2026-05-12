import os
import html
from pathlib import Path
import xml.etree.ElementTree as ET

GT_DIR      = 'svg_GT'
OUTPUTS_DIR = 'extracted_outputs/svg'
EVAL_DIR    = 'evaluation/svg'
OUTPUT_HTML = 'evaluation_summary_svg.html'

def remove_namespace(elem):
    if '}' in elem.tag:
        elem.tag = elem.tag.split('}', 1)[1]
    for child in list(elem):
        remove_namespace(child)
        
def count_elements():
    splits = [20, 40, 60, 80, 100]
    filenames_split = [[] for i in range(len(splits)+1)]
    svg_paths = list(Path(GT_DIR).rglob('*.svg'))
    for svg_path in svg_paths:
        try:
            tree = ET.parse(svg_path)
            root = tree.getroot()
            remove_namespace(root)
        except ET.ParseError as e:
            print(f"Warning: Could not parse {svg_path}: {e}")
            return None
        tags = ['circle', 'ellipse', 'line', 'polygon', 'polyline']
        num_elements = sum(len(root.findall(f'.//{tag}')) for tag in tags)
        for i, split in enumerate(splits):
            if num_elements <= split:
                filenames_split[i].append(os.path.basename(svg_path))
                break
        if num_elements > splits[-1]:
            filenames_split[len(splits)].append(os.path.basename(svg_path))

    return filenames_split

def main():
                    
    filenames = sorted([
        fn for fn in os.listdir(GT_DIR)
        if fn.lower().endswith('.svg') and os.path.isfile(os.path.join(GT_DIR, fn))
    ])
            
    models = sorted([
        d for d in os.listdir(OUTPUTS_DIR)
        if os.path.isdir(os.path.join(OUTPUTS_DIR, d))
    ])

    filenames_split = count_elements()

    accuracies = {}
    accuracies_count = {}
    for m in models:
        correct = 0
        total = 0
        for fn in filenames:
            base, _ = os.path.splitext(fn)
            eval_file = os.path.join(EVAL_DIR, m, f"{base}.txt")
            total += 1
            if os.path.exists(eval_file):
                txt = open(eval_file, 'r', encoding='utf-8').read().strip()
                if txt == '1':
                    correct += 1
        accuracies[m] = (correct / total) if total > 0 else 0.0

        accuracies_count[m] = [0 for _ in range(len(filenames_split))]
        for i, filenames_ in enumerate(filenames_split):
            correct = 0
            total = 0
            for fn in filenames_:
                base, _ = os.path.splitext(fn)
                eval_file = os.path.join(EVAL_DIR, m, f"{base}.txt")
                total += 1
                if os.path.exists(eval_file):
                    txt = open(eval_file, 'r', encoding='utf-8').read().strip()
                    if txt == '1':
                        correct += 1
            accuracies_count[m][i] = (correct / total) if total > 0 else 0.0

    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
                           
        f.write("""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <title>SVG evaluation summary</title>
  <style>
    .table-container { overflow: auto; max-height: 80vh; }
    table { border-collapse: collapse; width: 100%; }
    th, td { border: 1px solid #ccc; padding: 6px; vertical-align: top; text-align: center; }
    th { background: #f0f0f0; position: sticky; top: 0; z-index: 3; }
    th:first-child, td:first-child {
      position: sticky; left: 0; background: #f0f0f0; z-index: 2;
      max-width: 120px; white-space: normal; word-wrap: break-word; overflow-wrap: break-word;
    }
    th:first-child { z-index: 4; }
    img { width: 500px; height: auto; display: block; margin: 0 auto; }
    .correct { color: red; font-weight: bold; }
  </style>
</head>
<body>
  <h1>SVG evaluation summary</h1>
  <div class="table-container">
    <table>
""")
                                                     
        f.write("    <tr>\n")
        f.write("      <th></th>\n")
        f.write("      <th>GT</th>\n")
        for m in models:
            p = accuracies[m]
            p2 = "["
            for acc in accuracies_count[m]:
                p2 += f"{acc:.2%}/"
            p2 += "]"
            f.write(f"      <th>{html.escape(m)}<br>Accuracy {p:.1%}<br>" + p2 + "</th>\n")
        f.write("    </tr>\n")

        for fn in filenames:
            base, _ = os.path.splitext(fn)
            f.write("    <tr>\n")
                        
            f.write(f"      <th>{html.escape(fn)}</th>\n")

            gt_path = os.path.join(GT_DIR, fn)
            f.write("      <td>\n")
            f.write(f'        <a href="{gt_path.replace("%27","%2527").replace("#","%23")}">'
                    f'<img src="{gt_path.replace("%27","%2527").replace("#","%23")}" alt="GT"></a>\n')
            f.write("        <div>reference</div>\n")
            f.write("      </td>\n")

            for m in models:
                out_svg   = os.path.join(OUTPUTS_DIR, m, fn).replace(".svg", ".response.svg")
                eval_file = os.path.join(EVAL_DIR, m, f"{base}.txt")
                f.write("      <td>\n")
                if os.path.exists(out_svg):
                         
                    f.write(f'        <a href="{out_svg.replace("%27","%2527").replace("#","%23")}">'
                            f'<img src="{out_svg.replace("%27","%2527").replace("#","%23")}" alt="{m}"></a>\n')
                        
                    if os.path.exists(eval_file):
                        txt = open(eval_file, 'r', encoding='utf-8').read().strip()
                        if txt == '1':
                            f.write('        <div class="correct">correct</div>\n')
                        elif txt == '0':
                            f.write('        <div>incorrect</div>\n')
                        else:
                            f.write(f'        <div>{html.escape(txt)}</div>\n')
                    else:
                        f.write('        <div>not found</div>\n')
                else:
                    f.write('        <div>not found</div>\n')
                f.write("      </td>\n")

            f.write("    </tr>\n")

        f.write("""  </table>
  </div>
</body>
</html>
""")

    print(f"Generated {OUTPUT_HTML}")

if __name__ == '__main__':
    main()
