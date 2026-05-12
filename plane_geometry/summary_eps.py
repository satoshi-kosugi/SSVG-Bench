                      

import os
import subprocess
import resource
from PyPDF2 import PdfReader

GT_DIR       = 'eps_GT'
OUTPUTS_DIR  = 'extracted_outputs/eps'
EVAL_DIR     = 'evaluation/eps'
OUTPUT_TEX   = 'evaluation_summary_eps.tex'
OUTPUT_PDF   = 'evaluation_summary_eps.pdf'

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

    accuracies = {}
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

        headers = ['File', 'Ref'] + [r"\begin{tabular}{c}" + f"{m.replace('_', ' ')}" + r"\\" + str(accuracies[m]*100)[:5] + r"\end{tabular}" for m in models]
        f.write(' & '.join(headers) + r' \\' + '\n')
        f.write(r'\hline' + '\n')

        for i, fn in enumerate(filenames):
            base, _ = os.path.splitext(fn)
            row = []

            row.append(fn.replace("_", "\_").replace("%", "\%").replace("#", "\#").replace("é", "e"))

            gt_path = os.path.join(GT_DIR, fn)
            if os.path.exists(gt_path):
                row.append(
                    r'\includegraphics[width=3cm, page=1]{' +
                    escape_tex(gt_path) +
                    r'}'
                )
            else:
                row.append('not found')

            for m in models:
                out_pdf   = os.path.join(OUTPUTS_DIR, m, fn)
                eval_file = os.path.join(EVAL_DIR, m, f"{base}.txt")

                cell = r'\begin{tabular}{c}'
                                                                                    
                if os.path.exists(out_pdf):
                    cell += r'\includegraphics[width=3cm, page=1]{' + escape_tex(out_pdf) + r'}'
                if os.path.exists(eval_file):
                    txt = open(eval_file, 'r', encoding='utf-8').read().strip()
                    if txt == '1':
                        cell += r' \\ \color{red}\textbf{correct} \color{black}'
                    elif txt == '0':
                        cell += r' \\ incorrect'
                    else:
                        cell += r' \\ compilation error'
                                               
                else:
                    cell += r' \\ not found'

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
