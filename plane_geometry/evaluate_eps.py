                      
import os
import subprocess
import sys

def main():
                
    gt_dir        = 'eps_GT'
    outputs_base  = 'extracted_outputs/eps'
    evals_base    = 'evaluation/eps'

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

            out_eps = os.path.join(llm_out_dir, fname)

            out_pdf = os.path.join(llm_out_dir, fname.replace(".eps", ".pdf"))

            if fname.endswith('.response.eps'):
                base = fname[:-len('.response.eps')]
            else:
                base = fname[:-len('.eps')]

            eval_txt = os.path.join(llm_eval_dir, f'{base}.txt')
            if os.path.exists(eval_txt):
                continue
            
            if os.path.exists(out_pdf):
                gt_eps = os.path.join(gt_dir, f'{base}.svg')
                if not os.path.isfile(gt_eps):
                    print(f'Warning: ground-truth not found for {base}', file=sys.stderr)
                    continue

                if os.path.exists(os.path.join("evaluation_code/eps/", f'{base}.py')):
                    evaluation_code_path = os.path.join("evaluation_code/eps/", f'{base}.py')
                else:
                    evaluation_code_path = 'evaluation_code/eps/evaluate_eps_base.py'

                try:
                    completed = subprocess.run(
                        ['python', evaluation_code_path, gt_eps, out_eps],
                        check=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                except subprocess.CalledProcessError as e:
                    print(f'Error evaluating {out_eps}:\n{e.stderr}', file=sys.stderr)
                    continue

                result = completed.stdout.strip()               
            elif not os.path.isfile(out_eps):
                result = 'eps does not exist'
                print(out_eps, 'does not exist', file=sys.stderr)
            else:
                result = 'pdf does not exist'
                print(out_pdf, 'does not exist', file=sys.stderr)

            with open(eval_txt, 'w', encoding='utf-8') as f:
                f.write(result + '\n')

            print(f'Evaluated {llm_name}/{base}: {result}')

if __name__ == '__main__':
    main()
