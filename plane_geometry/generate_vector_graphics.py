import os
import re
import argparse

import openai
from openai import OpenAI
import anthropic
from google import genai
import time

OPENAI_API_KEY = "###"
ANTHROPIC_API_KEY = "###"
GEMINI_API_KEY = "###"
DEEPSEEK_API_KEY = "###"

def strip_urls(text: str) -> str:
                            
    return re.sub(r'https?://\S+', '', text)

def prepare_prompt(text_path: str, vector_path: str, vector_type: str) -> str:
                                               
    with open(text_path, 'r', encoding='utf-8') as f:
        explanation = strip_urls(f.read()).strip()

    with open(vector_path, 'r', encoding='utf-8') as f:
        vector = f.read().strip()

    if vector_type == "svg":
        prompt = f"""[Explanation]{explanation}
[SVG]{vector}
Please visualize the explanation by adding elements to the SVG diagram.
- Assign class="output_text" to any added text elements, and class="output_object" to all other added elements.
- Do not modify any elements that are originally present in the SVG.
– Do not use any animations."""
    elif vector_type == "tex":
        prompt = f"""[Explanation]{explanation}
[TikZ]{vector}
Please visualize the explanation by adding elements to the TikZ diagram.
– Set the color of any added elements to red.
– Do not modify any elements that are originally present in the TikZ.
– Do not use any animations."""
    elif vector_type == "eps":
        prompt = f"""[Explanation]{explanation}
[EPS]{vector}
Please visualize the explanation by adding elements to the EPS diagram.
– Set the color of any added elements to red.
– Do not modify any elements that are originally present in the EPS.
– Do not use any animations."""
    return prompt

def call_model(model_name: str, prompt: str) -> str:
\
\

    if model_name in ('o3-mini-2025-01-31', 'o4-mini-2025-04-16'):
        openai.api_key = OPENAI_API_KEY
        resp = openai.chat.completions.create(
            model=model_name,
            reasoning_effort="high",
            messages=[{'role': 'user', 'content': prompt}]
        )
        return resp.choices[0].message.content.strip()

    elif model_name in ('gpt-4.1-2025-04-14'):
        openai.api_key = OPENAI_API_KEY
        resp = openai.chat.completions.create(
            model=model_name,
            messages=[{'role': 'user', 'content': prompt}]
        )
        return resp.choices[0].message.content.strip()

    elif model_name in ('gpt-5-main'):
        openai.api_key = OPENAI_API_KEY
        resp = openai.chat.completions.create(
            model='gpt-5-chat-latest',
            messages=[{'role': 'user', 'content': prompt}]
        )
        return resp.choices[0].message.content.strip()

    elif model_name in ('gpt-5-thinking'):
        openai.api_key = OPENAI_API_KEY
        resp = openai.chat.completions.create(
            model='gpt-5',
            messages=[{'role': 'user', 'content': prompt}]
        )
        return resp.choices[0].message.content.strip()

    elif model_name in ('gpt-5.1-chat-latest'):
        openai.api_key = OPENAI_API_KEY
        resp = openai.chat.completions.create(
            model='gpt-5.1-chat-latest',
            messages=[{'role': 'user', 'content': prompt}]
        )
        return resp.choices[0].message.content.strip()

    elif model_name in ('gpt-5.1-2025-11-13'):
        openai.api_key = OPENAI_API_KEY
        resp = openai.chat.completions.create(
            model='gpt-5.1-2025-11-13',
            messages=[{'role': 'user', 'content': prompt}],
            reasoning_effort="high",

        )
        return resp.choices[0].message.content.strip()

    elif model_name in ('gpt-5.2-chat-latest'):
        openai.api_key = OPENAI_API_KEY
        resp = openai.chat.completions.create(
            model='gpt-5.2-chat-latest',
            messages=[{'role': 'user', 'content': prompt}]
        )
        return resp.choices[0].message.content.strip()

    elif model_name in ('gpt-5.3-chat-latest'):
        openai.api_key = OPENAI_API_KEY
        resp = openai.chat.completions.create(
            model='gpt-5.3-chat-latest',
            messages=[{'role': 'user', 'content': prompt}]
        )
        return resp.choices[0].message.content.strip()

    elif model_name in ('gpt-5.2-2025-12-11'):
        openai.api_key = OPENAI_API_KEY
        resp = openai.chat.completions.create(
            model='gpt-5.2-2025-12-11',
            messages=[{'role': 'user', 'content': prompt}],
            reasoning_effort="high",
        )
        return resp.choices[0].message.content.strip()

    elif model_name in ('gpt-5.4-2026-03-05'):
        openai.api_key = OPENAI_API_KEY
        resp = openai.chat.completions.create(
            model='gpt-5.4-2026-03-05',
            messages=[{'role': 'user', 'content': prompt}],
            reasoning_effort="high",
        )
        return resp.choices[0].message.content.strip()

    elif model_name.startswith('claude-3-7-sonnet'):
        client = anthropic.Client(api_key=ANTHROPIC_API_KEY)
                                                                                
        if "thinking" in model_name:
            resp = client.messages.create(
                model="claude-3-7-sonnet-20250219",
                max_tokens=4096,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                thinking= {
                    "type": "enabled",
                    "budget_tokens": 3277,
                },
                )
            return resp.content[0].thinking + "/n" + resp.content[1].text
        else:
            resp = client.messages.create(
                model="claude-3-7-sonnet-20250219",
                max_tokens=4096,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                )
            return resp.content[0].text

    elif model_name.startswith('claude-opus-4-1'):
        client = anthropic.Client(api_key=ANTHROPIC_API_KEY)
                                                                                
        if "thinking" in model_name:
            resp = client.messages.create(
                model="claude-opus-4-1-20250805",
                max_tokens=8192,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                thinking= {
                    "type": "enabled",
                    "budget_tokens": 4096,
                },
                )
            return resp.content[0].thinking + "/n" + resp.content[1].text
        else:
            resp = client.messages.create(
                model="claude-opus-4-1-20250805",
                max_tokens=4096,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                )
            return resp.content[0].text

    elif model_name.startswith('claude-opus-4-5'):
        client = anthropic.Client(api_key=ANTHROPIC_API_KEY)
                                                                                
        if "thinking" in model_name:
            resp = client.messages.create(
                model="claude-opus-4-5-20251101",
                max_tokens=20000,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                thinking= {
                    "type": "enabled",
                    "budget_tokens": 16000,
                },
                )
            return resp.content[0].thinking + "/n" + resp.content[1].text
        else:
            resp = client.messages.create(
                model="claude-opus-4-5-20251101",
                max_tokens=20000,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                )
            return resp.content[0].text

    elif model_name.startswith('claude-opus-4-6'):
        client = anthropic.Client(api_key=ANTHROPIC_API_KEY)
                                                                                
        if "thinking" in model_name:
            resp = client.messages.create(
                model="claude-opus-4-6",
                max_tokens=20000,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                thinking= {
                    "type": "enabled",
                    "budget_tokens": 16000,
                },
                )
            return resp.content[0].thinking + "/n" + resp.content[1].text
        else:
            resp = client.messages.create(
                model="claude-opus-4-6",
                max_tokens=20000,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                )
            return resp.content[0].text

    elif model_name.startswith('gemini'):
        client = genai.Client(api_key=GEMINI_API_KEY)
        for attempt in range(1, 10 + 1):
            try:
                if model_name == "gemini-2.5-flash":
                    response = client.models.generate_content(
                        model="gemini-2.5-flash", contents=prompt,
                        config=genai.types.GenerateContentConfig(
                            thinking_config=genai.types.ThinkingConfig(thinking_budget=0)
                        ),
                    )
                elif model_name == "gemini-2.5-flash-reasoning":
                    response = client.models.generate_content(
                        model="gemini-2.5-flash", contents=prompt,
                    )
                elif model_name == "gemini-2.5-pro":
                    response = client.models.generate_content(
                        model="gemini-2.5-pro", contents=prompt,
                    )
                elif model_name == "gemini-3-flash-preview":
                    response = client.models.generate_content(
                        model="gemini-3-flash-preview", contents=prompt,
                    )
                elif model_name == "gemini-3-pro-preview":
                    response = client.models.generate_content(
                        model="gemini-3-pro-preview", contents=prompt,
                    )
                elif model_name == "gemini-3.1-pro-preview":
                    response = client.models.generate_content(
                        model="gemini-3.1-pro-preview", contents=prompt,
                    )
                if response.text is None:
                    continue
                else:
                    break
            except Exception as e:
                print(e.args)
                time.sleep(60)
        return response.text

    elif model_name.startswith('DeepSeek'):
        client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")
        messages = [{"role": "user", "content": prompt}]
        if "DeepSeek-V-3-2-reasoning" == model_name:
            response = client.chat.completions.create(
                model="deepseek-reasoner",
                messages=messages
            )
            reasoning_content = response.choices[0].message.reasoning_content
            content = response.choices[0].message.content
            return reasoning_content + "\n" + content
        elif "DeepSeek-V-3-2" == model_name:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=messages
            )
            content = response.choices[0].message.content
            return content
    else:
        raise ValueError(f"Unsupported model: {model_name}")

def main():
    parser = argparse.ArgumentParser(
        description='Collect outputs from various LLMs for vector visualization tasks.'
    )
    parser.add_argument(
        '--model', '-m',
        required=True,
        choices=[
            'o3-mini-2025-01-31', 'o4-mini-2025-04-16', 'gpt-4.1-2025-04-14',
            'gpt-5-main', 'gpt-5-thinking',
            'gpt-5.1-2025-11-13', 'gpt-5.1-chat-latest',
            'gpt-5.2-2025-12-11', 'gpt-5.2-chat-latest',
            'gpt-5.4-2026-03-05', 'gpt-5.3-chat-latest',
            'claude-3-7-sonnet-20250219', 'claude-3-7-sonnet-20250219-thinking',
            'claude-opus-4-1', 'claude-opus-4-1-thinking',
            'claude-opus-4-5', 'claude-opus-4-5-thinking',
            'claude-opus-4-6', 'claude-opus-4-6-thinking',
            'gemini-2.5-flash-preview-04-17',
            'gemini-2.5-flash',
            'gemini-2.5-flash-reasoning',
            'gemini-2.5-pro',
            'gemini-2.0-flash', 
            'gemini-3-flash-preview', 
            'gemini-3-pro-preview', 
            'gemini-3.1-pro-preview',
            'DeepSeek-V-3-2', 'DeepSeek-V-3-2-reasoning'
        ],
        help='Which LLM model to use for inference.'
    )
    parser.add_argument(
        '--input-text-dir', default='explanation',
        help='Directory containing .txt files with scientific explanations.'
    )
    parser.add_argument(
        '--input-vector-dir', default='tikz_input',
        help='Directory containing base files.'
    )
    parser.add_argument(
        '--output-dir', default='outputs',
        help='Directory where outputs will be saved.'
    )

    args = parser.parse_args()

    if "svg" in args.input_vector_dir:
        vector_type = "svg"
    elif "tikz" in args.input_vector_dir:
        vector_type = "tex"
    elif "eps" in args.input_vector_dir:
        vector_type = "eps"
    else:
        raise NotImplementedError

    model_output_dir = os.path.join(args.output_dir, vector_type, args.model.replace(' ', '_'))
    os.makedirs(model_output_dir, exist_ok=True)

    for fname in sorted(os.listdir(args.input_text_dir)):
        base, ext = os.path.splitext(fname)
        if ext.lower() != '.txt':
            continue

        txt_path = os.path.join(args.input_text_dir, fname)
        vector_fname = f"{base}.{vector_type}"
        vector_path = os.path.join(args.input_vector_dir, vector_fname)

        if not os.path.isfile(vector_path):
            print(f"Skipping {fname}: no matching file found.")
            continue

        out_path = os.path.join(model_output_dir, f"{base}.response.txt")
        if os.path.exists(out_path):
            print(out_path, "already exists")
            continue

        prompt = prepare_prompt(txt_path, vector_path, vector_type)
        try:
            output = call_model(args.model, prompt)
        except Exception as e:
            print(f"Error querying model for {base}: {e}")
            continue

        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"Saved output for {base} to {out_path}")

if __name__ == '__main__':
    main()
