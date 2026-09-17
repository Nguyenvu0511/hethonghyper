# -*- coding: utf-8 -*-
with open('src/bot/handlers.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract the plan_today handler
start_str = '@router.message(Command("plan_today"))'
end_str = '# ---'
# Actually we can just find it using regex or split
parts = content.split('@router.message(Command("plan_today"))')
if len(parts) > 1:
    before = parts[0]
    handler_code = '@router.message(Command("plan_today"))' + parts[1]
    
    # We want to insert handler_code right BEFORE @router.message(F.text)
    # So we split before F.text
    sub_parts = before.split('@router.message(F.text)')
    
    if len(sub_parts) > 1:
        new_content = sub_parts[0] + handler_code + '\n' + '@router.message(F.text)' + sub_parts[1]
        with open('src/bot/handlers.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
            print("Moved handler up!")