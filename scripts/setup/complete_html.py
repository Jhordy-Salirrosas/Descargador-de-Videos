"""
Script para completar el nuevo index.html con todo el JavaScript del backup
"""

# Read backup file
with open('templates/index_backup.html', 'r', encoding='utf-8') as f:
    backup_content = f.read()

# Read new incomplete file  
with open('templates/index.html', 'r', encoding='utf-8') as f:
    new_content = f.read()

#Remove the placeholder comment
new_content = new_content.replace('<!-- Continue in next message due to size... -->', '')

# Extract JavaScript section from backup (from '<script>' to '</html>')
backup_lines = backup_content.split('\n')
script_lines = []
capturing = False
for i, line in enumerate(backup_lines):
    if '<script>' in line and i > 300:  # Start from script tag after line 300
        capturing = True
    if capturing:
        script_lines.append(line)

# Join the script lines
script_section = '\n'.join(script_lines)

# Append to new file
complete_content = new_content + '\n' + script_section

# Write completed file
with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(complete_content)

print(f"✓ Completed! Added {len(script_lines)} lines of JavaScript")
print(f"Total file size: {len(complete_content)} characters")
