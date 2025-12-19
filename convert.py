import os
import re
import json

def parse_markdown_files(directory):
    data = {}
    
    # Regex 1: (Q01.01) Question Text
    q_pattern_std = re.compile(r'^\((Q\d+\.\d+)\)\s*(.*)')
    # Regex 2: > (1) Question Text (used in Q02)
    q_pattern_alt = re.compile(r'^>\s*\((\d+)\)\s*(.*)')
    
    for filename in os.listdir(directory):
        if not filename.endswith('.md'):
            continue
            
        filepath = os.path.join(directory, filename)
        
        # Use filename as topic name reference
        # "Q01 - Name.md" -> "Q01 - Name"
        topic_key = filename.replace('.md', '')
        
        # Extract Prefix (Q01, Q02) for ID generation if needed
        # Match start of string Q\d+
        prefix_match = re.match(r'^(Q\d+)', topic_key)
        topic_prefix = prefix_match.group(1) if prefix_match else "QXX"

        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        current_questions = []
        current_q = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            match_std = q_pattern_std.match(line)
            match_alt = q_pattern_alt.match(line)
            
            if match_std or match_alt:
                # Save previous question if exists
                if current_q:
                    current_questions.append(current_q)
                
                if match_std:
                    full_id = match_std.group(1)
                    q_text = match_std.group(2).strip()
                else:
                    # Alternate format: > (1) -> Q02.01, > (10) -> Q02.10
                    # Check if match.group(1) is single digit
                    num_str = match_alt.group(1)
                    num = num_str.zfill(2) # '1'->'01', '10'->'10'
                    full_id = f"{topic_prefix}.{num}"
                    q_text = match_alt.group(2).strip()
                
                current_q = {
                    "id": full_id,
                    "question": q_text,
                    "answer": ""
                }
            else:
                # content line - append to current question answer
                
                # Regex for markdown image: ![alt](url)
                # We need to prepend 'topics/' to url if it doesn't have it (assuming relative to md file)
                # And convert to <img ...>
                
                def img_replacer(match):
                    alt = match.group(1)
                    url = match.group(2)
                    # Adjust path: img/foo.png -> topics/img/foo.png
                    # Check if it starts with http or topics already
                    if not url.startswith('http') and not url.startswith('topics/'):
                        url = f"topics/{url}"
                    return f'<img src="{url}" alt="{alt}">'

                line = re.sub(r'!\[(.*?)\]\((.*?)\)', img_replacer, line)

                if current_q:
                    # Append line with newline to preserve some formatting
                    if current_q["answer"]:
                        current_q["answer"] += "\n" + line
                    else:
                        current_q["answer"] = line

        # Let's refactor the loop slightly to handle image replacement cleanly.
        # But since I must use replace_file_content, I will stick to the plan of injecting logic.
        # I'll replace the block where 'line' is processed as content.
        
        # ACTUALLY, I see I made a mistake in the thought process trying to fit it in "replacementContent".
        # I should just replace the "else: # content line" block.


        # Append the last question
        if current_q:
            current_questions.append(current_q)
            
        if current_questions:
            data[topic_key] = current_questions

    return data

if __name__ == "__main__":
    target_dir = "topics" 
    output_file = "data.js" # Changed to JS to avoid CORS on local file protocol
    
    result = parse_markdown_files(target_dir)
    
    # Write as a JS file with a global variable
    with open(output_file, 'w', encoding='utf-8') as f:
        json_str = json.dumps(result, indent=2, ensure_ascii=False)
        f.write(f"window.appData = {json_str};")
    
    print(f"Converted {len(result)} topics to {output_file}")
