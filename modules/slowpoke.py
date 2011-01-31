# -*- coding: utf-8 -*-
__module_class_names__ = ["Slowpoke"]

from mate import MateModule
import time

class Slowpoke(MateModule):
    def __init__(self, mate, config):
        MateModule.__init__(self, mate, config)
        self.regex = mate.conf['nick'] + ': slowpoke'
        self.conf['threadable'] = True
        self.conf['thread_timeout'] = 1.0

    def run(self, mate, nick, msg):
        mate.reply('Slooooow...')
        time.sleep(8.0)
        mate.reply('...poke')
