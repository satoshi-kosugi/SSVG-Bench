import os
import re
import subprocess
from urllib.parse import unquote

def extract_and_compile_tex(
    input_root='outputs/tex',
    output_root='extracted_outputs/tex',
    original_root='tikz_input/'
):
                                                                        
    tex_pattern = re.compile(
        r'(\\documentclass\{standalone\}[\s\S]*?\\end\{document\})',
        re.DOTALL
    )
    tex_pattern2 = re.compile(
        r'(\\begin\{tikzpicture\}[\s\S]*?\\end\{tikzpicture\})',
        re.DOTALL
    )
    tex_pattern3 = re.compile(
        r'(```latex[\s\S]*?\```)',
        re.DOTALL
    )
    tex_pattern4 = re.compile(
        r'(\\documentclass\[tikz\]\{standalone\}[\s\S]*?\\end\{document\})',
        re.DOTALL
    )
    tex_pattern5 = re.compile(
        r'(```tikz\n\\documentclass[\s\S]*?\\end\{document\}\n```)',
        re.DOTALL
    )
    tex_pattern6 = re.compile(
        r'(```tex[\s\S]*?\```)',
        re.DOTALL
    )

    for subdir in sorted(os.listdir(input_root)):
        subdir_path = os.path.join(input_root, subdir)
        if not os.path.isdir(subdir_path):
            continue

        out_subdir = os.path.join(output_root, subdir)
        os.makedirs(out_subdir, exist_ok=True)

        for filename in sorted(os.listdir(subdir_path)):
            print(filename)
            if not filename.endswith('.response.txt'):
                continue

            raw_basename = filename[:-len('.response.txt')]
            decoded      = unquote(raw_basename)
            safe_basename= re.sub(r'[^\w\-]', '_', decoded)
            tex_file = os.path.join(out_subdir, f'{safe_basename}.tex')

            if os.path.exists(tex_file):
                continue

            input_file = os.path.join(subdir_path, filename)
            with open(input_file, 'r', encoding='utf-8') as f:
                content = f.read()

            match3 = tex_pattern3.findall(content)
            match5 = tex_pattern5.findall(content)
            match6 = tex_pattern6.findall(content)
            match = tex_pattern.findall(content)
            if len(match3) != 0:
                tex_content = match3[-1].replace("```latex", "").replace("```", "")
            elif len(match5) != 0:
                tex_content = match5[-1].replace("```tikz", "").replace("```", "")
            elif len(match6) != 0:
                tex_content = match6[-1].replace("```tex", "").replace("```", "")
            elif len(match) != 0:
                tex_content = match[-1]
            else:
                                                       
                matches2 = tex_pattern2.findall(content)
                                                          
                matches4 = tex_pattern4.findall(content)
                if len(matches4) != 0:
                    tex_content = matches4[-1]
                elif len(matches2) != 0:

                    tex_content = r"""\documentclass{standalone}
\usepackage{tikz}
\usetikzlibrary{calc, intersections}
\begin{document}""" + matches2[-1] + r"\end{document}"

                else:
                    print(f'No TeX block found in {input_file}')
                                                   
                    continue

            if r"\usetikzlibrary{calc}" not in tex_content:
                tex_content = tex_content.replace(r"\begin{document}", r"\usetikzlibrary{calc, intersections}"+"\n"+r"\begin{document}")
           
            if r"\documentclass{standalone}" in tex_content and not r"\documentclass[tikz]{standalone}" in tex_content:
                tex_content = tex_content.replace(r"\documentclass{standalone}", r"\documentclass[tikz]{standalone}")

            with open(tex_file, 'w', encoding='utf-8') as out_f:
                out_f.write(tex_content)
            print(f'Saved TeX to {tex_file}')

            success = True
            try:
                subprocess.run(
                    ['pdflatex', '-interaction=batchmode', "-output-directory="+out_subdir, tex_file],
                    check=True,
                    timeout=10,
                                    
                )
                print(f'Compiled {tex_file} to PDF')
            except subprocess.CalledProcessError as e:
                success = False
                print(f'Error compiling {tex_file}: {e}')
            except subprocess.TimeoutExpired as e:
                success = False
                print(f'Error compiling {tex_file}: {e}')

            if os.path.exists(os.path.join(out_subdir, safe_basename + '.pdf')):
                if success:
                    os.replace(
                        os.path.join(out_subdir, safe_basename + '.pdf'),
                        os.path.join(out_subdir, raw_basename + '.pdf')
                    )
                    try:
                        subprocess.run(
                            ['pdf2svg', os.path.join(out_subdir, raw_basename + '.pdf'), os.path.join(out_subdir, raw_basename + '.svg')],
                            check=True,
                            timeout=10,
                                            
                        )
                    except subprocess.CalledProcessError as e:
                        pass
                else:
                    os.replace(
                        os.path.join(out_subdir, safe_basename + '.pdf'),
                        os.path.join(out_subdir, "failed" + '.pdf')
                    )

if __name__ == '__main__':
    extract_and_compile_tex()
