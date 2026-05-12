import os
import re
import subprocess

def extract_and_compile_eps(
    input_root='outputs/eps',
    output_root='extracted_outputs/eps',
    original_root='eps_input/'
):
                                                                           
    eps_pattern = re.compile(
        r'(%!PS-Adobe-3\.0 EPSF-3\.0[\s\S]*?showpage)',
        re.DOTALL
    )
    eps_pattern2 = re.compile(
        r'(```eps[\s\S]*?\```)',
        re.DOTALL
    )
    eps_pattern2_ = re.compile(
        r'(```postscript[\s\S]*?\```)',
        re.DOTALL
    )
    eps_pattern3 = re.compile(
        r'(```[\s\S]*?\```)',
        re.DOTALL
    )
    eps_pattern4 = re.compile(
        r'data:image/eps;base64,([A-Za-z0-9+/=\r\n]+)'
    )

    for subdir in os.listdir(input_root):
        subdir_path = os.path.join(input_root, subdir)
        if not os.path.isdir(subdir_path):
            continue

        out_subdir = os.path.join(output_root, subdir)
        os.makedirs(out_subdir, exist_ok=True)

        for filename in os.listdir(subdir_path):
            if not filename.endswith('.response.txt'):
                continue

            input_file = os.path.join(subdir_path, filename)
            with open(input_file, 'r', encoding='utf-8') as f:
                content = f.read()

            base_name = filename[:-len('.response.txt')]
            eps_file = os.path.join(out_subdir, f'{base_name}.eps')
            if os.path.exists(eps_file):
                continue

            match = eps_pattern.findall(content)
            if len(match) != 0:
                eps_content = match[-1]
            else:
                matches2 = list(eps_pattern2.finditer(content))
                matches2_ = list(eps_pattern2_.finditer(content))
                matches3 = list(eps_pattern3.finditer(content))
                matches4 = list(eps_pattern4.finditer(content))
                if len(matches2) != 0:
                    original_file = os.path.join(original_root, filename.replace(".response.txt", ".eps"))
                    with open(original_file, 'r', encoding='utf-8') as f:
                        original_content = f.read()
                    eps_content = matches2[-1].group(0)
                    eps_content = eps_content.replace("```eps", "").replace("```", "")
                    eps_content = original_content.replace("showpage", eps_content+"\n showpage")
                elif len(matches2_) != 0:
                    original_file = os.path.join(original_root, filename.replace(".response.txt", ".eps"))
                    with open(original_file, 'r', encoding='utf-8') as f:
                        original_content = f.read()
                    eps_content = matches2_[-1].group(0)
                    eps_content = eps_content.replace("```postscript", "").replace("```", "")
                    eps_content = original_content.replace("showpage", eps_content+"\n showpage")
                elif len(matches3) != 0:
                    original_file = os.path.join(original_root, filename.replace(".response.txt", ".eps"))
                    with open(original_file, 'r', encoding='utf-8') as f:
                        original_content = f.read()
                    eps_content = matches3[-1].group(0)
                    eps_content = eps_content.replace("```", "")
                    eps_content = original_content.replace("showpage", eps_content+"\n showpage")
                elif len(matches4) != 0:
                    import base64
                    b64_content = matches4[-1].group(0).replace("data:image/eps;base64,", "")
                    raw = base64.b64decode(b64_content)
                    try:
                        eps_content = raw.decode('utf-8')
                    except UnicodeDecodeError:
                                                          
                        eps_content = raw.decode('latin1')

                else:
                    print(f'No EPS block found in {input_file}')
                    continue

            with open(eps_file, 'w', encoding='utf-8') as out_f:
                out_f.write(eps_content)
            print(f'Saved EPS to {eps_file}')

            pdf_file = os.path.join(out_subdir, f'{base_name}.pdf')
            success = True
            try:
                subprocess.run(
                    ['epstopdf', eps_file, f'--outfile={pdf_file}'],
                    check=True
                )

                subprocess.run(
                    ['pdf2svg', pdf_file, pdf_file.replace('.pdf', '.svg')],
                    check=True,
                    timeout=10,
                                    
                )
                print(f'Compiled {eps_file} to {pdf_file}')
            except subprocess.CalledProcessError as e:
                success = False
                print(f'Error compiling {eps_file}: {e}')

            if os.path.exists(pdf_file) and (not success):
                os.replace(
                    os.path.join(pdf_file),
                    os.path.join(out_subdir, "failed.pdf")
                )
if __name__ == '__main__':
    extract_and_compile_eps()
