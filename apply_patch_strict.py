import re

with open('dashboard/style.css', 'r') as f:
    target_lines = f.read().splitlines()

with open('reverse.patch', 'r') as f:
    patch_lines = f.read().splitlines()

hunks = []
current_hunk = None
for line in patch_lines:
    if line.startswith('@@'):
        if current_hunk:
            hunks.append(current_hunk)
        m = re.match(r'@@ -(\d+),?(\d*) \+(\d+),?(\d*) @@', line)
        if m:
            old_start, old_len, new_start, new_len = m.groups()
            old_len = int(old_len) if old_len else 1
            new_start = int(new_start)
            new_len = int(new_len) if new_len else 1
            current_hunk = {
                'new_start': new_start,
                'new_len': new_len,
                'lines': []
            }
    elif current_hunk is not None:
        current_hunk['lines'].append(line)

if current_hunk:
    hunks.append(current_hunk)

# Apply from bottom to top to avoid line shift issues
hunks.reverse()

for hunk in hunks:
    start_idx = hunk['new_start'] - 1
    new_len = hunk['new_len']
    
    # Extract the lines that should replace the old lines
    replacement_lines = []
    for line in hunk['lines']:
        if line.startswith('-'):
            replacement_lines.append(line[1:])
        elif line.startswith(' '):
            replacement_lines.append(line[1:])
    
    # Replace the section in the target file
    target_lines[start_idx : start_idx + new_len] = replacement_lines

with open('dashboard/style.css', 'w') as f:
    f.write('\n'.join(target_lines) + '\n')
