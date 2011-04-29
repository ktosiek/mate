# -*- coding: utf-8 -*-
__module_class_names__ = ["GraczRuletki"]

from mate import MateModule

class GraczRuletki(MateModule):
    def __init__(self, mate, config):
        MateModule.__init__(self, mate, config)
        self.regex = '(?i)(' + mate.conf['nick'] + ': teraz ty([!]*))|(^\.krec)$'
        self.ready = False

    def run(self, mate, nick, msg):
        if not self.ready and '.krec' in mate.match:
            self.ready = True
        elif self.ready and not '.krec' in mate.match:
            mate.say( '.strzal' )
            self.ready = False
        elif not self.ready and not '.krec' in mate.match:
            mate.reply( 'a takiego wała' )

