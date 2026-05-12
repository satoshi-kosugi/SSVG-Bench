import os
import re
import argparse

import openai
from openai import OpenAI
import anthropic
from google import genai
import time
import json

OPENAI_API_KEY = "###"
ANTHROPIC_API_KEY = "###"
GEMINI_API_KEY = "###"
DEEPSEEK_API_KEY = "###"

def strip_urls(text: str) -> str:
                            
    return re.sub(r'https?://\S+', '', text)

def prepare_prompt(iupac_name: str, vector_type: str) -> str:

    if vector_type == "svg":
        template_file_name = "svg_template.txt"
    elif vector_type == "tex":
        template_file_name = "tikz_template.txt"
    elif vector_type == "eps":
        template_file_name = "eps_template.txt"

    with open(template_file_name, 'r', encoding='utf-8') as f:
        template = f.read()
    prompt = template.replace("[iupac_name]", iupac_name)
    return prompt

def _anthropic_text_from_content(content) -> str:
    """Extract text/thinking blocks from an Anthropic message response."""
    parts = []
    for block in content:
        if getattr(block, "type", None) == "thinking" and hasattr(block, "thinking"):
            parts.append(block.thinking)
        elif getattr(block, "type", None) == "text" and hasattr(block, "text"):
            parts.append(block.text)
        elif hasattr(block, "text"):
            parts.append(block.text)
    return "\n".join(part for part in parts if part).strip()

def call_model(model_name: str, prompt: str) -> str:
                   
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

    elif model_name.startswith(('claude-opus-4-1', 'claude-opus-4-5', 'claude-opus-4-6')):
        client = anthropic.Client(api_key=ANTHROPIC_API_KEY)

        if model_name.startswith('claude-opus-4-1'):
            api_model = "claude-opus-4-1-20250805"
            max_tokens = 8192 if "thinking" in model_name else 4096
            thinking_budget = 4096
        elif model_name.startswith('claude-opus-4-5'):
            api_model = "claude-opus-4-5-20251101"
            max_tokens = 20000
            thinking_budget = 16000
        else:
            api_model = "claude-opus-4-6"
            max_tokens = 20000
            thinking_budget = 16000

        create_kwargs = dict(
            model=api_model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        if "thinking" in model_name:
            create_kwargs["thinking"] = {
                "type": "enabled",
                "budget_tokens": thinking_budget,
            }

        resp = client.messages.create(**create_kwargs)
        return _anthropic_text_from_content(resp.content)

    elif model_name.startswith('gemini'):
        client = genai.Client(api_key=GEMINI_API_KEY)
        gemini_model_map = {
            "gemini-2.5-flash-reasoning": "gemini-2.5-flash",
            "gemini-2.5-flash-preview-04-17": "gemini-2.5-flash-preview-04-17",
            "gemini-2.5-flash": "gemini-2.5-flash",
            "gemini-2.5-pro": "gemini-2.5-pro",
            "gemini-2.0-flash": "gemini-2.0-flash",
            "gemini-3-flash-preview": "gemini-3-flash-preview",
            "gemini-3-pro-preview": "gemini-3-pro-preview",
            "gemini-3.1-pro-preview": "gemini-3.1-pro-preview",
        }
        api_model = gemini_model_map.get(model_name)
        if api_model is None:
            raise ValueError(f"Unsupported Gemini model: {model_name}")

        response = None
        for attempt in range(1, 10 + 1):
            try:
                if model_name == "gemini-2.5-flash":
                    response = client.models.generate_content(
                        model=api_model,
                        contents=prompt,
                        config=genai.types.GenerateContentConfig(
                            thinking_config=genai.types.ThinkingConfig(thinking_budget=0)
                        ),
                    )
                else:
                    response = client.models.generate_content(
                        model=api_model,
                        contents=prompt,
                    )
                if response.text is not None:
                    break
            except Exception as e:
                print(e.args)
                time.sleep(60)
        else:
            raise RuntimeError(f"Failed to get a non-empty response from {model_name}")

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
            'gemini-3-flash-preview',
            'gemini-3-pro-preview',
            'gemini-3.1-pro-preview',
            'gemini-2.0-flash', 

            'DeepSeek-V-3-2', 'DeepSeek-V-3-2-reasoning'
        ],
        help='Which LLM model to use for inference.'
    )
    parser.add_argument(
        '--vector-type',
        required=True,
        choices=[
            'svg', 'eps', 'tex',
        ],
    )
    parser.add_argument(
        '--output-dir', default='outputs',
        help='Directory where outputs will be saved.'
    )
    parser.add_argument(
        '--prompting', default=None,
        help='Optional suffix used in the output directory name.'
    )

    args = parser.parse_args()

    vector_type = args.vector_type

    if args.prompting is None:
        model_output_dir = os.path.join(args.output_dir, vector_type, args.model.replace(' ', '_'))
    else:
        model_output_dir = os.path.join(args.output_dir, vector_type, args.model.replace(' ', '_')+"_"+args.prompting)
    os.makedirs(model_output_dir, exist_ok=True)

    with open("pubchem_compounds_filtered.json", "r", encoding="utf-8") as f:
        compounds = json.load(f)

    for compound in compounds:
        iupac_name = compound["iupac_name"]
        cid = compound["cid"]

        out_path = os.path.join(model_output_dir, f"{cid}.response.txt")
        if os.path.exists(out_path):
            print(out_path, "already exists")
            continue

        prompt = prepare_prompt(iupac_name, vector_type)
        try:
            output = call_model(args.model, prompt)
        except Exception as e:
            print(f"Error querying model for {cid}: {e}")
            continue

        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"Saved output for {cid} to {out_path}")

if __name__ == '__main__':
    main()
