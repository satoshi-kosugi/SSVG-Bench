import os
import re
import subprocess

def extract_and_compile_eps(
    input_root='outputs/eps',
    output_root='extracted_outputs/eps',
                                
):
                                                                           
    eps_pattern = re.compile(
        r'(%[ \t]*!PS-Adobe-3\.0 EPSF-3\.0[\s\S]*?showpage)',
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
    eps_pattern2__ = re.compile(
        r'(```ps[\s\S]*?\```)',
        re.DOTALL
    )
    eps_pattern2___ = re.compile(
        r'(```PostScript[\s\S]*?\```)',
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

            base_name = filename[:-len('.response.txt')]
            eps_file = os.path.join(out_subdir, f'{base_name}.eps')

            if os.path.exists(eps_file):
                continue

            input_file = os.path.join(subdir_path, filename)
            with open(input_file, 'r', encoding='utf-8') as f:
                content = f.read()

            match = eps_pattern.findall(content)
            matches2 = list(eps_pattern2.finditer(content))
            matches2_ = list(eps_pattern2_.finditer(content))
            matches2__ = list(eps_pattern2__.finditer(content))
            matches2___ = list(eps_pattern2___.finditer(content))
            matches3 = list(eps_pattern3.finditer(content))
            matches4 = list(eps_pattern4.finditer(content))

            if ("```" not in content) and len(match) != 0:
                                 
                eps_content = match[-1]
            elif len(matches2) != 0:
                eps_content = matches2[-1].group(0)
                eps_content = eps_content.replace("```eps", "").replace("```", "")
            elif len(matches2_) != 0:
                eps_content = matches2_[-1].group(0)
                eps_content = eps_content.replace("```postscript", "").replace("```", "")
            elif len(matches2__) != 0:
                eps_content = matches2__[-1].group(0)
                eps_content = eps_content.replace("```ps", "").replace("```", "")
            elif len(matches2___) != 0:
                eps_content = matches2___[-1].group(0)
                eps_content = eps_content.replace("```PostScript", "").replace("```", "")
            elif len(matches3) != 0:
                eps_content = matches3[-1].group(0)
                eps_content = eps_content.replace("```", "")
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

            BB_PATTERN = re.compile(
                r'^(%%BoundingBox:)\s+'
                r'([-+]?\d*\.?\d+)\s+'
                r'([-+]?\d*\.?\d+)\s+'
                r'([-+]?\d*\.?\d+)\s+'
                r'([-+]?\d*\.?\d+)$',
                re.MULTILINE
            )
            def repl(m: re.Match) -> str:
                prefix = m.group(1)
                                                        
                ints = [str(int(float(m.group(i)))) for i in range(2, 6)]
                return f"{prefix} {' '.join(ints)}"
            
            eps_content = BB_PATTERN.sub(repl, eps_content)

            if len(eps_content) > 0:
                idx = eps_content.find('%')
                if idx != -1:
                    eps_content = eps_content[idx:]

            with open(eps_file, 'w', encoding='utf-8') as out_f:
                out_f.write(eps_content)
            print(f'Saved EPS to {eps_file}')

            pdf_file = os.path.join(out_subdir, f'{base_name}.pdf')
            success = True
            try:
                subprocess.run(
                    ['epstool', '--copy', '--bbox', eps_file, '--output', eps_file.replace(".eps", "_fixed.eps")],
                    check=True,
                    timeout=10
                )
                subprocess.run(
                    ['epstopdf', eps_file.replace(".eps", "_fixed.eps"), f'--outfile={pdf_file}'],
                    check=True,
                    timeout=10
                )
                print(f'Compiled {eps_file} to {pdf_file}')
            except subprocess.CalledProcessError as e:
                success = False
                print(f'Error compiling {eps_file}: {e}')
            except subprocess.TimeoutExpired  as e:
                success = False
                print(f'Error compiling {eps_file}: {e}')

            if os.path.exists(pdf_file):
                if success:
                    subprocess.run(
                        ['pdf2svg', pdf_file, pdf_file.replace(".pdf", '.svg')],
                        check=True,
                        timeout=10,
                                        
                    )
                else:
                    os.replace(
                        os.path.join(pdf_file),
                        os.path.join(out_subdir, "failed.pdf")
                    )

if __name__ == '__main__':
    extract_and_compile_eps()
