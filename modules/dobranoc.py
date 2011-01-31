# -*- coding: utf-8 -*-
__module_class_names__ = ["Slowpoke"]

from mate import MateModule, run_per_minute, noop
import time

class Slowpoke(MateModule):
    def __init__(self, mate, config):
        MateModule.__init__(self, mate, config)
        self.regex = '(?i)((^| |do|\')branoc|goodnight|(^| )g\'n( |$))'

    @run_per_minute(1, noop)
    def run(self, mate, nick, msg):
        mate.say('dobranoc %s' % nick)
