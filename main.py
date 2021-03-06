#!/usr/bin/env python3

from mate import *
import logging

config = { 'server': 'hake5.selfip.net',
           'port': 6660,
           'nick': 'Pyton',
           'realname': 'Pyton; owner: tomekk',
           'ssl': True,
           'channels': ['#bot'],
           'owner': 'tomekk',
           'module_blacklist': ['slowpoke'],
           }

if __name__ == '__main__':
    logging.basicConfig(filename = '/home/tomek/.mate/log', level=logging.DEBUG, \
                        format="%(levelname)s %(asctime)s %(funcName)s %(lineno)d %(message)s")

    mate = Mate(config)
    mate.main()
