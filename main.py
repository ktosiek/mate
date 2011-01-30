#!/usr/bin/env python

from mate import *

config = { 'server': 'hake5.selfip.net',
           'port': 6660,
           'nick': 'Pyton',
           'realname': 'Pyton; owner: tomekk',
           'ssl': True,
           'channels': ['#bot'],
           }

if __name__ == '__main__':

    mate = Mate(config)
    mate.main()
