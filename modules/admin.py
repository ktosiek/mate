# -*- coding: utf-8 -*-
from mate import MateModule

__module_class_names__ = ["Reload", "IrcCmd"]
__module_config__ = { 'admins': (['tomekk'],
                                 list,
                                 """ List of administrators """),
                      }

class Reload(MateModule):
    def __init__(self, mate, config):
        MateModule.__init__(self, mate, config)
        self.regex = mate.conf['nick'] + u': (reload|unload) ([a-zA-Z0-9_]*)( ([a-zA-Z0-9]+))*'

    def run(self, mate, nick, msg):
        """
        mate: instancja Mate
        nick: nick osoby której wypowiedź pasowała
        msg: dopasowana wiadomość
        """
        if not nick in self.conf['admins']:
            mate.say('sorry %s, I don\'t think I can do that' % nick)
            return

        action = mate.match.group(1)
        pack_name = mate.match.group(2)
        modules = mate.match.group(4)
        if action == 'reload':
            action_str = u'Reloading %s'
        elif action == 'unload':
            action_str = u'Unloading %s'

        if modules == None:
            print action_str % (pack_name)
        else:
            print (action_str +' : %s') % (pack_name, list(modules))
        
        mate.unload_module( pack_name, modules )
        if action == 'reload':
            mate.load_module( pack_name, modules )

class IrcCmd(MateModule):
    def __init__(self, mate, config):
        MateModule.__init__(self, mate, config)
        self.regex = mate.conf['nick'] + u': (irccmd|ctcp) (.*)'

    def run(self, mate, nick, msg):
        if not nick in self.conf['admins']:
            mate.say('sorry %s, I don\'t think I can do that' % nick)
            return

        print 'irccmd'
        args = mate.match.groups()
        cmd = args[0]
        params = args[1].split(' ')

        if cmd == 'irccmd':
            full_cmd = params
        elif cmd == 'ctcp':
            full_cmd = ['PRIVMSG', params[0], u'' + chr(1) + ' '.join(params[1:]) + chr(1)]

        print 'IrcCmd: %s: %s' % ( cmd, full_cmd )
        mate.irc.cmd(full_cmd)
