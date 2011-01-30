# -*- coding: utf-8 -*-
__module_class_names__ = ["Hello", "Party"]

from mate import MateModule, run_per_minute, noop

class Hello(MateModule):
    def __init__(self, mate, config):
        MateModule.__init__(self, mate, config)
        self.regex = u'(?i)((hi|hello|hey|cześć|czesc|joł|jol|yo|omg)? *)' + mate.conf['nick'] + '(!*)$'

    def run(self, mate, nick, msg):
        if nick == 'Grazyna':
            mate.say( mate.match.group(1) + nick + mate.match.group(3) )
        else:
            mate.say( 'sssSSSSss ' + nick + mate.match.group(3) )

class Party(MateModule):
    def __init__(self, mate, config):
        MateModule.__init__(self, mate, config)
        self.regex = u'(?i).*party.*'

    def run(self, mate, nick, msg):
        mate.say( 'Party! Party! Party!' )
