                      
import os
import subprocess
import sys

def main():
                
    gt_dir        = 'svg_GT'
    outputs_base  = 'extracted_outputs/svg'
    evals_base    = 'evaluation/svg'

    os.makedirs(evals_base, exist_ok=True)

    for llm_name in os.listdir(outputs_base):
        llm_out_dir = os.path.join(outputs_base, llm_name)
        if not os.path.isdir(llm_out_dir):
            continue

        llm_eval_dir = os.path.join(evals_base, llm_name)
        os.makedirs(llm_eval_dir, exist_ok=True)

        for fname in sorted(os.listdir(llm_out_dir)):
            if not fname.endswith('.svg'):
                continue

            out_svg = os.path.join(llm_out_dir, fname)

            if fname.endswith('.response.svg'):
                base = fname[:-len('.response.svg')]
            else:
                base = fname[:-len('.svg')]
            eval_txt = os.path.join(llm_eval_dir, f'{base}.txt')

            if os.path.exists(eval_txt):
                print("passing:", eval_txt)
                continue

            gt_svg = os.path.join(gt_dir, f'{base}.svg')
            if not os.path.isfile(gt_svg):
                print(f'Warning: ground-truth not found for {base}', file=sys.stderr)
                continue

            if os.path.exists(os.path.join("evaluation_code/svg/", f'{base}.py')):
                evaluation_code_path = os.path.join("evaluation_code/svg/", f'{base}.py')
            else:
                evaluation_code_path = 'evaluation_code/svg/evaluate_svg_base.py'

            try:
                completed = subprocess.run(
                    ['python', evaluation_code_path, gt_svg, out_svg],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
            except subprocess.CalledProcessError as e:
                print(f'Error evaluating {out_svg}:\n{e.stderr}', file=sys.stderr)
                continue

            result = completed.stdout.strip()               

            with open(eval_txt, 'w', encoding='utf-8') as f:
                f.write(result + '\n')

            print(f'Evaluated {llm_name}/{base}: {result}')

if __name__ == '__main__':
    main()
