import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect('157.66.100.11', username='root', password='@Sieutoc!s@d2aZuRy4p*')
    
    stdin, stdout, stderr = ssh.exec_command("cd ~/hethonghyper && systemctl status mydtu_bot | head -n 15")
    
    with open('vps_status.txt', 'wb') as f:
        f.write(stdout.read())
        f.write(b'\n---\n')
        f.write(stderr.read())

finally:
    ssh.close()