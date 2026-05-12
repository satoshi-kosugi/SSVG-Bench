import os
import subprocess
import resource
from PyPDF2 import PdfReader
import PyPDF2
from pathlib import Path
import xml.etree.ElementTree as ET

GT_DIR       = 'tikz_GT'
OUTPUTS_DIR  = 'extracted_outputs/tex'
EVAL_DIR     = 'evaluation/tex'
OUTPUT_TEX   = 'evaluation_summary_tikz.tex'
OUTPUT_PDF   = 'evaluation_summary_tikz.pdf'

def remove_namespace(elem):
    if '}' in elem.tag:
        elem.tag = elem.tag.split('}', 1)[1]
    for child in list(elem):
        remove_namespace(child)
        
def count_elements():
    splits = [20, 40, 60, 80, 100]
    filenames_split = [[] for i in range(len(splits)+1)]
    svg_paths = list(Path('svg_GT').rglob('*.svg'))
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

def escape_tex(s: str) -> str:
                                                          
    return r'\detokenize{' + s.replace("_", "\_").replace("%", "\%").replace("#", "\#") + '}'

def main():
                    
    filenames = sorted([
        fn for fn in os.listdir(GT_DIR)
        if fn.lower().endswith('.pdf') and os.path.isfile(os.path.join(GT_DIR, fn))
    ])

    models = sorted([
        d for d in os.listdir(OUTPUTS_DIR)
        if os.path.isdir(os.path.join(OUTPUTS_DIR, d))
    ])

    filenames_split = count_elements()

    accuracies = {}
    accuracies_count = {}
    compile_errors_count = {}
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
        compile_errors_count[m] = [0 for _ in range(len(filenames_split))]
        for i, filenames_ in enumerate(filenames_split):
            correct = 0
            compile_error = 0
            total = 0
            for fn in filenames_:
                base, _ = os.path.splitext(fn)
                eval_file = os.path.join(EVAL_DIR, m, f"{base}.txt")
                total += 1
                if os.path.exists(eval_file):
                    txt = open(eval_file, 'r', encoding='utf-8').read().strip()
                    if txt == '1':
                        correct += 1
                    elif txt == "pdf does not exist":
                        compile_error += 1
            accuracies_count[m][i] = (correct / total) if total > 0 else 0.0
            compile_errors_count[m][i] = compile_error

    with open(OUTPUT_TEX, 'w', encoding='utf-8') as f:
        f.write(r'\pdfinclusionerrorlevel=1' + '\n')
        f.write(r'\documentclass[a2paper,10pt,landscape]{article}' + '\n')
        f.write(r'\usepackage[margin=20truemm]{geometry}' + '\n')
        f.write(r'\usepackage[utf8]{inputenc}' + '\n')
        f.write(r'\usepackage{graphicx}' + '\n')
        f.write(r'\usepackage{float}' + '\n')
        f.write(r'\usepackage{array}' + '\n')
        f.write(r'\usepackage{color}' + '\n')
        f.write(r'\begin{document}' + '\n\n')

        col_spec = '|' + 'l|' + 'c|' * (len(models) + 1)
        f.write(r'\begin{table}[H]' + '\n')
        f.write(r'\centering' + '\n')
        f.write(r'\resizebox{\textwidth}{!}{%' + '\n')
        f.write(r'\begin{tabular}{' + col_spec + '}' + '\n')
        f.write(r'\hline' + '\n')

        headers = ['File', 'Ref']
        for m in models:
            p2 = ""
            for acc in accuracies_count[m]:
                p2 += str(acc) + "/"
            p2 += ""
            headers += [r"\begin{tabular}{c}" + f"{m.replace('_', ' ')}" + r"\\" + str(accuracies[m]*100)[:5] + r"\\" + p2 + r"\end{tabular}"]
        f.write(' & '.join(headers) + r' \\' + '\n')
        f.write(r'\hline' + '\n')

        for i, fn in enumerate(filenames):
            base, _ = os.path.splitext(fn)
            row = []

            row.append(fn.replace("_", "\_").replace("%", "\%").replace("#", "\#").replace("é", "e"))

            gt_path = os.path.join(GT_DIR, fn)
            if os.path.exists(gt_path):
                row.append(
                    r'\includegraphics[height=3cm,width=3cm,keepaspectratio,page=1]{' +
                    escape_tex(gt_path) +
                    r'}'
                )
            else:
                row.append('not found')

            for m in models:
                out_pdf   = os.path.join(OUTPUTS_DIR, m, fn)
                eval_file = os.path.join(EVAL_DIR, m, f"{base}.txt")

                cell = r'\begin{tabular}{c}'
                try:
                    if os.path.exists(out_pdf) and len(PdfReader(out_pdf).pages) == 1:
                        cell += r'\includegraphics[height=3cm,width=3cm,keepaspectratio,page=1]{' + escape_tex(out_pdf) + r'}'
                    if os.path.exists(eval_file):
                        txt = open(eval_file, 'r', encoding='utf-8').read().strip()
                        if txt == '1':
                            cell += r' \\ \color{red}\textbf{correct} \color{black}'
                        elif txt == '0':
                            cell += r' \\ incorrect'
                        else:
                            cell += r' \\ compilation error'
                    else:
                                                  
                        cell += r' \\ compilation error'
                except PyPDF2.errors.EmptyFileError:
                    cell += r' \\ compilation error'

                cell += r'\end{tabular}'
                row.append(cell)

            f.write(' & '.join(row) + r' \\' + '\n')
            f.write(r'\hline' + '\n')

            if i != 0 and i%5 == 0:
                f.write(r'\end{tabular}' + '\n')
                f.write(r'}' + '\n')                            
                f.write(r'\end{table}' + '\n\n')

                f.write(r'\begin{table}[H]' + '\n')
                f.write(r'\centering' + '\n')
                f.write(r'\resizebox{\textwidth}{!}{%' + '\n')                        
                f.write(r'\begin{tabular}{' + col_spec + '}' + '\n')
                f.write(r'\hline' + '\n')
                headers = ['File', 'Ref'] + [r"\begin{tabular}{c}" + f"{m.replace('_', ' ')}" + r"\\" + str(accuracies[m]*100)[:5] + r"\end{tabular}" for m in models]
                f.write(' & '.join(headers) + r' \\' + '\n')
                f.write(r'\hline' + '\n')

        f.write(r'\end{tabular}' + '\n')
        f.write(r'}' + '\n')
        f.write(r'\end{table}' + '\n\n')
        f.write(r'\end{document}' + '\n')

    soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
    resource.setrlimit(resource.RLIMIT_NOFILE, (8192, hard))
                     
    subprocess.run([
        'pdflatex',
        '-interaction=nonstopmode',
        OUTPUT_TEX
    ], check=True)

    print(f"Generated {OUTPUT_PDF}")

if __name__ == '__main__':
    main()
