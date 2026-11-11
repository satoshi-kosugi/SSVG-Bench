# SSVG-Bench #

This repository contains the official implementation of our paper published in IEEE Access. [[paper](https://ieeexplore.ieee.org/document/11783335)]

All the resources required for SSVG-Bench are provided, including input texts, ground-truth vector graphics, code for generating outputs using LLMs, and evaluation scripts.

## Requirements ##

Install the Python libraries:

```Shell
pip install -r requirements.txt
```

## Vector Graphic Generation by LLMs ##

The following steps should be performed after navigating to the appropriate directory:

```Shell
cd plane_geometry (or) cd molecular_structure
```
To generate vector graphics using LLMs, use `generate_vector_graphics.py`.
First, set the `API_KEY` inside `generate_vector_graphics.py`.

Then, run the script as shown below. The following example uses TikZ, but the same applies for SVG and EPS.
```Shell
(plane_geometry) python generate_vector_graphics.py --model gemini-3.1-pro-preview --input-text-dir explanation/ --input-vector-dir tikz_input/
(molecular_structure) python generate_vector_graphics.py --model gemini-3.1-pro-preview --vector-type tex
```

## Automatic Evaluation ##
To perform automatic evaluation, first extract the vector data from the LLM outputs:
```Shell
python extract_tikz.py
```

Next, run the evaluation:
```Shell
python evaluate_tikz.py
```

Finally, generate a summary of the vector graphics and evaluation results:
```Shell
python summary_tikz.py
```
