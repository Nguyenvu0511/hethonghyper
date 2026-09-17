import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect('157.66.100.11', username='root', password='@Sieutoc!s@d2aZuRy4p*')
    
    stdin, stdout, stderr = ssh.exec_command("cd ~/hethonghyper && git fetch origin && git reset --hard origin/main && systemctl restart mydtu_bot && systemctl status mydtu_bot | head -n 15")
    
    print(stdout.read().decode('utf-8', errors='ignore'))
    print(stderr.read().decode('utf-8', errors='ignore'))

finally:
    ssh.close()