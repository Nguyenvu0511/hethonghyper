import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    ssh.connect('157.66.100.11', username='root', password='@Sieutoc!s@d2aZuRy4p*')
    stdin, stdout, stderr = ssh.exec_command("ls -la ~/hethonghyper/data")
    print(stdout.read().decode('utf-8'))
finally:
    ssh.close()