import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    ssh.connect('157.66.100.11', username='root', password='@Sieutoc!s@d2aZuRy4p*')
    cmd = '''python3 -c "import sqlite3; conn=sqlite3.connect('/root/hethonghyper/data/learning_system.db'); print(conn.execute('SELECT name FROM sqlite_master WHERE type=\\"table\\"').fetchall()); print(conn.execute('SELECT * FROM users').fetchall())"'''
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print("Output:", stdout.read().decode('utf-8'))
    print("Err:", stderr.read().decode('utf-8'))
finally:
    ssh.close()