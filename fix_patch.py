import re

with open('dashboard/style.css', 'r') as f:
    content = f.read()

with open('reverse.patch', 'r') as f:
    patch_lines = f.read().splitlines()

# Parse the diff
hunks = []
current_hunk = None
for line in patch_lines:
    if line.startswith('@@'):
        if current_hunk:
            hunks.append(current_hunk)
        current_hunk = []
    elif current_hunk is not None:
        current_hunk.append(line)

if current_hunk:
    hunks.append(current_hunk)

# For each hunk, extract the "new" text (context + added) and "old" text (context + removed)
# and do a string replace in the content
new_content = content
for hunk in hunks:
    old_lines = []
    new_lines = []
    for line in hunk:
        if line.startswith('-'):
            old_lines.append(line[1:])
        elif line.startswith('+'):
            new_lines.append(line[1:])
        elif line.startswith(' '):
            old_lines.append(line[1:])
            new_lines.append(line[1:])
        else:
            # edge cases, e.g., EOF newline missing
            pass
            
    old_str = '\n'.join(old_lines)
    new_str = '\n'.join(new_lines)
    
    if new_str in new_content:
        new_content = new_content.replace(new_str, old_str, 1)
    else:
        # fuzzy replace if trailing newline differs
        if new_str + '\n' in new_content:
            new_content = new_content.replace(new_str + '\n', old_str + '\n', 1)
        elif new_str.strip() in new_content.strip():
            print("Found stripped match")

with open('dashboard/style.css', 'w') as f:
    f.write(new_content)

print("Patch applied")
