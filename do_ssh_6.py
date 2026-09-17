import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect('157.66.100.11', username='root', password='@Sieutoc!s@d2aZuRy4p*')
    
    # We need to discard the local changes I made on the VPS earlier with fix_rate_limit.py
    stdin, stdout, stderr = ssh.exec_command("cd ~/hethonghyper && git reset --hard HEAD && git pull origin main && systemctl restart mydtu_bot")
    print("Pull:", stdout.read().decode('utf-8', errors='ignore'))
    print(stderr.read().decode('utf-8', errors='ignore'))
    
    time.sleep(5)
    
    stdin, stdout, stderr = ssh.exec_command("systemctl status mydtu_bot | head -n 15")
    status = stdout.read().decode('utf-8', errors='ignore')
    print("Status:", status)
    
    if "active (running)" not in status:
        stdin, stdout, stderr = ssh.exec_command("journalctl -u mydtu_bot.service -n 20 --no-pager")
        print("Logs:", stdout.read().decode('utf-8', errors='ignore'))

finally:
    ssh.close()