# -*- coding: utf-8 -*-
from mate import MateModule

__module_class_names__ = ["AntiGerhard"]
__module_config__ = { 'combos': (['gerh', 'gerhard', 'schr', 'schroeder'],
                                 list,
                                 """ List of combos to break """),
                      'anycombo': (True,
                                   bool,
                                   """ Turn anycombo-mode on - this will break any stream of 1-char long messages of length anycombo_max_len """),
                      'anycombo_msgs': (5,
                                        int,
                                        """ Max. number of 1-char long messages """),
                      }

class AntiGerhard(MateModule):
    def __init__(self, mate, config):
        MateModule.__init__(self, mate, config)
        self.regex = u'.*'

        if self.conf['anycombo']:
            self.anycombo_msgs_so_far = 0

        self.last_combo = ''
        self.over_one_message = False

    def run(self, mate, nick, msg):
        if self.conf['anycombo']:
            if len(msg) == 1:
                self.anycombo_msgs_so_far += 1
                if self.anycombo_msgs_so_far >= self.conf['anycombo_msgs']:
                    mate.say('c-c-combo breaker!')
                    self.anycombo_msgs_so_far = 0
            else:
                self.anycombo_msgs_so_far = 0

        for char in msg:
            self.last_combo += char
            go_on = False
            for c in self.conf['combos']:
                if c.upper().startswith( self.last_combo.upper() ):
                    go_on = True
                    if c.upper() == self.last_combo.upper():
                        if self.over_one_message:
                            mate.say('c-c-combo breaker!')
                            self.last_combo = ''
                            self.over_one_message = False
        if not go_on:
            self.last_combo = ''
            self.over_one_message = False
        if len(self.last_combo) > 0:
            self.over_one_message = True

