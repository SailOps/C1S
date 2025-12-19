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
        
        table_buffer = []

        def flush_table(buffer):
            if not buffer:
                return ""
            
            # Check for header separator (row 2 starts with | - or | :-)
            has_header = False
            if len(buffer) > 1 and re.match(r'^\|\s*:?-+', buffer[1].strip()):
                has_header = True
            
            html = '<div class="table-container"><table>'
            
            start_idx = 0
            if has_header:
                # Process Header
                header_row = buffer[0].strip().strip('|').split('|')
                html += '<thead><tr>'
                for cell in header_row:
                    html += f'<th>{cell.strip()}</th>'
                html += '</tr></thead>'
                start_idx = 2 # Skip header and separator
            
            html += '<tbody>'
            for i in range(start_idx, len(buffer)):
                row_line = buffer[i].strip()
                # Skip separator if it wasn't caught (e.g. malformed)
                if re.match(r'^\|\s*:?-+', row_line):
                    continue
                    
                cells = row_line.strip('|').split('|')
                html += '<tr>'
                for cell in cells:
                    html += f'<td>{cell.strip()}</td>'
                html += '</tr>'
            html += '</tbody></table></div>'
            return html

        for line in lines:
            line = line.strip()
            if not line:
                # Even empty lines might break a table in markdown, usually.
                # Let's flush table if empty line is encountered
                if table_buffer:
                     if current_q:
                        current_q["answer"] += flush_table(table_buffer)
                     table_buffer = []
                continue
                
            match_std = q_pattern_std.match(line)
            match_alt = q_pattern_alt.match(line)
            
            if match_std or match_alt:
                # Flush table before new question
                if table_buffer:
                     if current_q:
                        current_q["answer"] += flush_table(table_buffer)
                     table_buffer = []

                # Save previous question if exists
                if current_q:
                    current_questions.append(current_q)
                
                if match_std:
                    full_id = match_std.group(1)
                    q_text = match_std.group(2).strip()
                else:
                    num_str = match_alt.group(1)
                    num = num_str.zfill(2)
                    full_id = f"{topic_prefix}.{num}"
                    q_text = match_alt.group(2).strip()
                
                current_q = {
                    "id": full_id,
                    "question": q_text,
                    "answer": ""
                }
            else:
                # Content line
                # Check for table row
                if line.startswith('|'):
                    table_buffer.append(line)
                    continue
                else:
                    # Not a table line, flush if needed
                    if table_buffer:
                        if current_q:
                             current_q["answer"] += flush_table(table_buffer)
                        table_buffer = []

                # Normal content processing
                
                def img_replacer(match):
                    alt = match.group(1)
                    url = match.group(2)
                    
                    if url.startswith('http'):
                        return f'<img src="{url}" alt="{alt}">'

                    corrected_url = url
                    if not url.startswith('topics/'):
                        corrected_url = f"topics/{url}"
                    
                    if not os.path.exists(corrected_url):
                        print(f"⚠️  MISSING IMAGE: {corrected_url} (in {filename})")
                        return f'<div class="error">[M] IMAGE NOT FOUND: {url}</div>'
                        
                    return f'<img src="{corrected_url}" alt="{alt}">'

                line = re.sub(r'!\[(.*?)\]\((.*?)\)', img_replacer, line)

                if current_q:
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
        # Flush table at end
        if table_buffer:
             if current_q:
                current_q["answer"] += flush_table(table_buffer)
        
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
