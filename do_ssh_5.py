import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect('157.66.100.11', username='root', password='@Sieutoc!s@d2aZuRy4p*')
    
    cmd = """
cat << 'EOF' > fix_rate_limit.py
with open('src/bot/main_bot.py', 'r', encoding='utf-8') as f:
    content = f.read()
old_cmd = 'await bot.set_my_commands(commands)'
new_cmd = '''try:
        await bot.set_my_commands(commands)
    except Exception as e:
        print(f"Không thể set commands (có thể do rate limit): {e}")'''
content = content.replace(old_cmd, new_cmd)
with open('src/bot/main_bot.py', 'w', encoding='utf-8') as f:
    f.write(content)
EOF
python3 fix_rate_limit.py
git commit -am "Fix: Ignore set_my_commands rate limit error on startup"
git push origin main
systemctl restart mydtu_bot
"""
    stdin, stdout, stderr = ssh.exec_command(f"cd ~/hethonghyper && {cmd}")
    
    with open('vps_logs.txt', 'wb') as f:
        f.write(stdout.read())
        f.write(stderr.read())

finally:
    ssh.close()