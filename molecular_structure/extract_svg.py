import os
import re

def extract_svgs(input_root='outputs/svg', output_root='extracted_outputs/svg'):
                                     
    svg_pattern_ = re.compile(r'(```xml\n<svg\r?[\s\S]*?</svg>\n)```')

    svg_pattern = re.compile(r'(<svg[\s\S]*?</svg>)', re.DOTALL)
    svg_pattern2 = re.compile(r'(```xml[\s\S]*?```)', re.DOTALL)

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
            output_file = os.path.join(out_subdir, f'{base_name}.response.svg')
            if os.path.exists(output_file):
                continue

            svgs = svg_pattern.findall(content)
            svgs_ = svg_pattern_.findall(content)

            if svgs_:
                svg_content = svgs_[-1]
                svg_content = svg_content.replace("```xml", "").replace("```", "")
            elif svgs:
                svg_content = svgs[-1]
                if svg_content.count("<svg") != 1:
                    svgs = svg_pattern.findall(svg_content[1:])
                    svg_content = svgs[-1]

            else:

                svg_content = ""

            svg_content = re.sub(r'([\w-]+="[^"]+")', r' \1 ', svg_content)

            with open(output_file, 'w', encoding='utf-8') as out_f:
                out_f.write(svg_content)
            print(f'Saved SVG to {output_file}')

if __name__ == '__main__':
    extract_svgs()
