import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    ssh.connect('157.66.100.11', username='root', password='@Sieutoc!s@d2aZuRy4p*')
    stdin, stdout, stderr = ssh.exec_command("journalctl -u mydtu_bot.service -n 20 --no-pager")
    print(stdout.read().decode('utf-8'))
finally:
    ssh.close()