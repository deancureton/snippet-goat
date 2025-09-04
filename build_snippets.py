import yaml
import json
import re
import os
import argparse
from dotenv import load_dotenv

def build_obsidian_snippets(snippets, verbatim_snippets, output_path):
    """
    builds the obsidian_snippets.js file from the snippets data
    """
    obsidian_snippets_data = []
    for snippet in snippets:
        target_platforms = snippet.get('target_platforms')
        if target_platforms and 'obsidian' not in target_platforms:
            continue

        obsidian_override = snippet.get('platforms', {}).get('obsidian', {})
        
        # start with base snippet, then apply platform override
        final_snippet = snippet.copy()
        final_snippet.update(obsidian_override)
        
        # deep merge options
        options = snippet.get('options', {}).copy()
        options.update(obsidian_override.get('options', {}))
        final_snippet['options'] = options

        # build options string
        opts_str = ""
        # if options.get('regex'): opts_str += 'r'
        if options.get('math'): opts_str += 'm'
        if options.get('inline_math'): opts_str += 'n'
        if options.get('display_math'): opts_str += 'M'
        if options.get('text'): opts_str += 't'
        if options.get('code'): opts_str += 'c'
        if options.get('auto'): opts_str += 'A'
        if options.get('visual'): opts_str += 'v'
        if options.get('word_boundary'): opts_str += 'w'
        final_snippet['options_str'] = opts_str
        
        # handle {{VAR}} syntax for obsidian native variables
        final_snippet['trigger'] = re.sub(r'\{\{(\w+)\}\}', r'${\1}', final_snippet['trigger'])

        obsidian_snippets_data.append(final_snippet)
    
    # generate the file content
    output_lines = []
    for s in obsidian_snippets_data:
        # json.dumps for safe string formatting (except for regex trigger)
        trigger_str = s['trigger']
        replacement_str = json.dumps(s['replacement'])
        options_str = json.dumps(s['options_str'])
        description_str = json.dumps(s.get('description', ''))

        line_parts = [
            f"trigger: /{trigger_str}/",
            f"replacement: {replacement_str}",
            f"options: {options_str}",
            f"description: {description_str}"
        ]

        if 'priority' in s:
            line_parts.append(f"priority: {s['priority']}")

        line = f"    {{ {', '.join(line_parts)} }}"
        output_lines.append(line)
    
    file_content = "[\n" + ",\n".join(output_lines)

    if verbatim_snippets.get('obsidian'):
        file_content += ",\n"
        verbatim_lines = [f"    {s.strip()}" for s in verbatim_snippets['obsidian']]
        file_content += ",\n".join(verbatim_lines)

    file_content += "\n]\n"

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(file_content)
    print(f"Successfully built {output_path}")

def build_obsidian_variables(variables, output_path):
    """
    builds the obsidian_variables.json file from the variables data
    """
    obsidian_vars = {f"${{{key}}}": value for key, value in variables.items()}
    with open(output_path, "w") as f:
        json.dump(obsidian_vars, f, indent=4)
    print(f"Successfully built {output_path}")

def build_latex_snippets(snippets, variables, verbatim_snippets, output_path):
    """
    builds the latex.hsnips file from the snippets data
    """
    hsnips_content = (
        "global\n"
        "function math(context) {\n"
        "    return context.scopes.findLastIndex(s => s.startsWith(\"meta.math\")) > context.scopes.findLastIndex(s => s.startsWith(\"comment\") || s.startsWith(\"meta.text.normal.tex\"));\n"
        "}\n"
        "function notmath(context) {\n"
        "    return context.scopes.findLastIndex(s => s.startsWith(\"meta.math\")) <= context.scopes.findLastIndex(s => s.startsWith(\"comment\") || s.startsWith(\"meta.text.normal.tex\"));\n"
        "}\n"
        "endglobal\n\n"
    )

    for snippet in snippets:
        # same stuff pretty much
        target_platforms = snippet.get('target_platforms')
        if target_platforms and 'vscode' not in target_platforms:
            continue

        vscode_override = snippet.get('platforms', {}).get('vscode', {})

        final_snippet = snippet.copy()
        final_snippet.update(vscode_override)
        
        options = snippet.get('options', {}).copy()
        options.update(vscode_override.get('options', {}))
        final_snippet['options'] = options

        trigger = final_snippet['trigger']

        # deal with {{VAR}} syntax for variables
        for var, val in variables.items():
            trigger = trigger.replace(f"{{{{{var}}}}}", val)
        
        replacement = final_snippet['replacement']
        # for hsnips, `\` is a special character in the body
        replacement = replacement.replace('\\', '\\\\')

        description = final_snippet.get('description', '')

        flags = ""
        if options.get('auto'): flags += 'A'
        if options.get('in_word'): flags += 'i'
        if options.get('word_boundary'): flags += 'w'
        if options.get('beginning_of_line'): flags += 'b'
        if options.get('multi_line'): flags += 'M'

        context = ""
        if options.get('math'):
            context = "context math(context)\n"
        elif options.get('text'):
            context = "context notmath(context)\n"

        snippet_str = ""
        if 'priority' in final_snippet:
            snippet_str += f"priority {final_snippet['priority']}\n"

        if context:
            snippet_str += context
        
        # add space between description and flags
        snippet_str += f'snippet `{trigger}` "{description}" {flags}\n'
        snippet_str += f'{replacement}\n'
        snippet_str += 'endsnippet\n\n'

        hsnips_content += snippet_str

    if verbatim_snippets.get('vscode'):
        for s in verbatim_snippets['vscode']:
            hsnips_content += f"{s.strip()}\n\n"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(hsnips_content)
    print(f"Successfully built {output_path}")

def resolve_path(path):
    """
    resolves a path, expanding ~ and making it absolute if it's not already
    """
    path = os.path.expanduser(path)
    if not os.path.isabs(path):
        return os.path.abspath(path)
    return path

def clean_files(paths):
    """
    deletes the files at the given paths
    """
    print(">>> Cleaning up generated files...")
    for path in paths:
        try:
            os.remove(path)
            print(f"    - Removed {path}")
        except FileNotFoundError:
            print(f"    - Not found, skipping: {path}")
        except Exception as e:
            print(f"    - Error removing {path}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Build or clean snippet files.")
    parser.add_argument('--clean', action='store_true', help='Remove generated snippet files.')
    args = parser.parse_args()

    load_dotenv()
    obsidian_path = resolve_path(os.getenv('OBSIDIAN_SNIPPETS_PATH', 'obsidian_snippets.js'))
    obsidian_vars_path = resolve_path(os.getenv('OBSIDIAN_VARIABLES_PATH', 'obsidian_variables.json'))
    latex_path = resolve_path(os.getenv('LATEX_SNIPPETS_PATH', 'latex.hsnips'))

    output_paths = [obsidian_path, obsidian_vars_path, latex_path]

    if args.clean:
        clean_files(output_paths)
        return

    with open("snippets.yaml", "r") as f:
        data = yaml.safe_load(f)
        snippets = data.get('snippets', [])
        variables = data.get('variables', {})
        verbatim_snippets = data.get('verbatim_snippets', {})

    build_obsidian_snippets(snippets, verbatim_snippets, obsidian_path)
    build_obsidian_variables(variables, obsidian_vars_path)
    build_latex_snippets(snippets, variables, verbatim_snippets, latex_path)

    print("Snippet build process completed.")

if __name__ == "__main__":
    main()
