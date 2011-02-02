# -*- coding: utf-8 -*-
__module_class_names__ = ["Ninja"]

from mate import MateModule, run_in_background
import time
import re

responses = { 'aiaiai': ['I am your butterfly', 'I need your protection', 'be my samurai'],
              'be my samurai': ['I\'m a ninja'],
              'enter ninja': ['he\'s the ninja: http://www.youtube.com/watch?v=wc3f4xU_FfQ'] }

class Ninja(MateModule):
    def __init__(self, mate, config):
        MateModule.__init__(self, mate, config)
        self.regex = u'(?i)('+ '|'.join( responses.keys() ) + ')'

    @run_in_background()
    def run(self, mate, nick, msg):
        for r in responses:
            if len(re.findall(r, msg)) > 0:
                my_responses = list( responses[r] )
                my_responses.reverse()
                while True:
                    mate.reply( my_responses.pop() )
                    if len(my_responses) > 0:
                        time.sleep(1.0)
                    else:
                        return
