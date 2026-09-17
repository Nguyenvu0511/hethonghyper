import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print("Connecting...")
    ssh.connect('157.66.100.11', username='root', password='@Sieutoc!s@d2aZuRy4p*')
    print("Connected! Running commands...")
    
    stdin, stdout, stderr = ssh.exec_command("cd ~/hethonghyper && git status && git pull origin main && systemctl restart mydtu_bot")
    print(stdout.read().decode())
    print(stderr.read().decode())
    
    # Check status
    stdin, stdout, stderr = ssh.exec_command("systemctl status mydtu_bot | head -n 15")
    print(stdout.read().decode())
    print(stderr.read().decode())

finally:
    ssh.close()