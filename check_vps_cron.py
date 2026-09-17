import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    ssh.connect('157.66.100.11', username='root', password='@Sieutoc!s@d2aZuRy4p*')
    # Grep logs between 13:40 and 13:50
    stdin, stdout, stderr = ssh.exec_command("journalctl -u mydtu_bot.service --since '2026-09-14 13:40:00' --until '2026-09-14 13:50:00'")
    print(stdout.read().decode('utf-8', errors='ignore'))
finally:
    ssh.close()