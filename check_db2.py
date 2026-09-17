import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect('157.66.100.11', username='root', password='@Sieutoc!s@d2aZuRy4p*')
    
    stdin, stdout, stderr = ssh.exec_command("sqlite3 ~/hethonghyper/data/learning_system.db 'SELECT task_id, target_time FROM tasks WHERE user_id = 1 AND frequency = \"daily\";'")
    print("Tasks:", stdout.read().decode('utf-8'))
finally:
    ssh.close()