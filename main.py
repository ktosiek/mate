#!/usr/bin/env python

from mate import *
import logging

config = { 'server': 'hake5.selfip.net',
           'port': 6660,
           'nick': 'Pyton',
           'realname': 'Pyton; owner: tomekk',
           'ssl': True,
           'channels': ['#bot'],
           'owner': ['tomekk'],
           'module_blacklist': ['slowpoke'],
           }

if __name__ == '__main__':
    logging.basicConfig(filename = '/home/tomek/.mate/log', level=logging.DEBUG)

    mate = Mate(config)
    mate.main()
