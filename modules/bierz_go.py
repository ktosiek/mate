#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
bierz_go.py - bierz go!
Author: Tomasz Kontusz
"""

__module_class_names__ = ["BierzGo"]

from mate import MateModule

class BierzGo(MateModule):
    def __init__(self, mate, config):
        MateModule.__init__(self, mate, config)
        self.last_nick = None

        self.regex = '(?i)' + mate.conf['nick']

    def run(self, mate, nick, msg):
        if 'bierz go' in msg:
            if self.last_nick == None:
                mate.say(nick + ': hssss!')
            else:
                mate.say(self.last_nick + ': hssss!')
        else:
            if nick == mate.conf['owner']:
                self.last_nick = None
            else:
                self.last_nick = nick

if __name__ == '__main__': 
   print(__doc__.strip())
