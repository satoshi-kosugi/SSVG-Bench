import os
import re

def extract_svgs(input_root='outputs/svg', output_root='extracted_outputs/svg'):
                                     
    svg_pattern = re.compile(r'(<svg [\s\S]*?</svg>)', re.DOTALL)
    svg_pattern2 = re.compile(r'(```xml[\s\S]*?```)', re.DOTALL)
    svg_pattern3 = re.compile(r'(```svg[\s\S]*?```)', re.DOTALL)

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
            output_file = os.path.join(out_subdir, f'{base_name}.response.svg')

            if os.path.exists(output_file):
                continue

            input_file = os.path.join(subdir_path, filename)
            with open(input_file, 'r', encoding='utf-8') as f:
                content = f.read()

            svgs = svg_pattern.findall(content)

            if svgs:
                svg_content = svgs[-1]
                if svg_content.count("<svg") != 1:
                    svgs = svg_pattern.findall(svg_content[1:])
                    svg_content = svgs[-1]

            else:
                match2 = svg_pattern2.search(content)
                match3 = svg_pattern3.search(content)
                if (not match2) and (not match3):
                    print(f'No <svg>...</svg> block found in {input_file}')
                    continue
                original_file = os.path.join("svg_input/", filename.replace(".response.txt", ".svg"))
                with open(original_file, 'r', encoding='utf-8') as f:
                    original_content = f.read()

                if match2:
                    svg_additional_content = match2.group(1).replace("```xml", "").replace("```", "")
                elif match3:
                    svg_additional_content = match3.group(1).replace("```svg", "").replace("```", "")

                svg_content = original_content.replace("</svg>", svg_additional_content+"</svg>")

            with open(output_file, 'w', encoding='utf-8') as out_f:
                out_f.write(svg_content)
            print(f'Saved SVG to {output_file}')

if __name__ == '__main__':
    extract_svgs()
