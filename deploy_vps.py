import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    ssh.connect('157.66.100.11', username='root', password='@Sieutoc!s@d2aZuRy4p*')
    ssh.exec_command("cd ~/hethonghyper && git pull origin main && systemctl restart mydtu_bot")
finally:
    ssh.close()