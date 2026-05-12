                      
import os
import subprocess
import sys
from urllib.parse import unquote
import re

def main():
                
    gt_dir        = 'tikz_GT'
    outputs_base  = 'extracted_outputs/tex'
    evals_base    = 'evaluation/tex'

    os.makedirs(evals_base, exist_ok=True)

    for llm_name in os.listdir(outputs_base):
        llm_out_dir = os.path.join(outputs_base, llm_name)
        if not os.path.isdir(llm_out_dir):
            continue

        llm_eval_dir = os.path.join(evals_base, llm_name)
        os.makedirs(llm_eval_dir, exist_ok=True)

        for fname in sorted(os.listdir(gt_dir)):
            if not fname.endswith('.svg'):
                continue

            out_tex = os.path.join(llm_out_dir, fname)

            out_pdf = os.path.join(llm_out_dir, fname.replace(".tex", ".pdf"))

            if fname.endswith('.response.tex'):
                base = fname[:-len('.response.tex')]
            else:
                base = fname[:-len('.tex')]

            eval_txt = os.path.join(llm_eval_dir, f'{base}.txt')
            if os.path.exists(eval_txt):
                continue

            if os.path.exists(out_pdf):
                gt_tex = os.path.join(gt_dir, f'{base}.svg')
                if not os.path.isfile(gt_tex):
                    print(f'Warning: ground-truth not found for {base}', file=sys.stderr)
                    continue

                if os.path.exists(os.path.join("evaluation_code/tex/", f'{base}.py')):
                    evaluation_code_path = os.path.join("evaluation_code/tex/", f'{base}.py')
                else:
                    evaluation_code_path = 'evaluation_code/tex/evaluate_tex_base.py'

                try:
                    completed = subprocess.run(
                        ['python', evaluation_code_path, gt_tex, out_tex],
                        check=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                except subprocess.CalledProcessError as e:
                    print(f'Error evaluating {out_tex}:\n{e.stderr}', file=sys.stderr)
                    continue

                result = completed.stdout.strip()               
            elif not os.path.isfile(out_tex):
                result = 'tex does not exist'
                print(out_tex, 'does not exist', file=sys.stderr)
            else:
                result = 'pdf does not exist'
                print(out_pdf, 'does not exist', file=sys.stderr)

            with open(eval_txt, 'w', encoding='utf-8') as f:
                f.write(result + '\n')

            print(f'Evaluated {llm_name}/{base}: {result}')

if __name__ == '__main__':
    main()
