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
        current_hunk = [line]
    elif current_hunk is not None:
        current_hunk.append(line)
if current_hunk:
    hunks.append(current_hunk)

for hunk in hunks:
    # Build the string to search for (the new lines + context)
    search_lines = []
    replace_lines = []
    for line in hunk[1:]:
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
        if search_str + '\n' in target_content:
            target_content = target_content.replace(search_str + '\n', replace_str + '\n', 1)
        else:
            print(f"Failed hunk: {hunk[0]}")
            # print search str to see what it is looking for
            print("Looking for:")
            print(repr(search_str))

with open('dashboard/style.css', 'w') as f:
    f.write(target_content)

print("Fuzzy patch applied")
