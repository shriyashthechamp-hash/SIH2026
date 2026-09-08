import re

with open('dashboard/style.css', 'r') as f:
    target_content = f.read()

with open('reverse.patch', 'r') as f:
    patch_lines = f.read().splitlines()

hunks = []
current_hunk = []
for line in patch_lines:
    if line.startswith('@@'):
        if current_hunk:
            hunks.append(current_hunk)
        current_hunk = []
    elif current_hunk is not None:
        current_hunk.append(line)
if current_hunk:
    hunks.append(current_hunk)

for hunk in hunks:
    # Build the string to search for (the new lines + context)
    search_lines = []
    replace_lines = []
    for line in hunk:
        if line.startswith('+'):
            search_lines.append(line[1:])
        elif line.startswith('-'):
            replace_lines.append(line[1:])
        elif line.startswith(' '):
            search_lines.append(line[1:])
            replace_lines.append(line[1:])
    
    search_str = '\n'.join(search_lines)
    replace_str = '\n'.join(replace_lines)
    
    if search_str in target_content:
        target_content = target_content.replace(search_str, replace_str, 1)
    else:
        # Try without the last newline
        if search_str + '\n' in target_content:
            target_content = target_content.replace(search_str + '\n', replace_str + '\n', 1)
        else:
            print("Failed to find exact match for hunk. Searching without context...")
            # If the context is slightly off, let's just find the exact block of + lines
            only_new = []
            for line in hunk:
                if line.startswith('+'):
                    only_new.append(line[1:])
            if only_new:
                only_new_str = '\n'.join(only_new)
                if only_new_str in target_content:
                    print("Found block of only + lines, but context didn't match. Manual replace needed.")

with open('dashboard/style.css', 'w') as f:
    f.write(target_content)

print("Fuzzy patch applied")
