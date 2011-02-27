# -*- coding: utf-8 -*-
__module_class_names__ = ["Wydupiaj"]

from mate import MateModule, run_per_minute, noop
import random

words_wydupiaj = [ 'wydupiaj', 'wypierdalaj', 'spierdalaj' ]
words_jebajsie = [ 'jebaj sie', 'jebaj się' ]

class Wydupiaj(MateModule):
    def __init__(self, mate, config):
        MateModule.__init__(self, mate, config)
        self.regex = '(?i)((' + '|'.join(words_wydupiaj + words_jebajsie) + ') *)(' + mate.conf['nick'] + ')([!?]*)$'

    def run(self, mate, nick, msg):
        if mate.match[1] in words_wydupiaj:
            mate.reply( random.choice( words_jebajsie ) )
        else:
            mate.reply( random.choice( words_wydupiaj) )

