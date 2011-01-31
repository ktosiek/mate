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
        self.regex = mate.conf['nick'] + u': (reload|unload) ([a-zA-Z0-9_]*)(( ([a-zA-Z0-9]+))*)'

    def run(self, mate, nick, msg):
        """
        mate: instancja Mate
        nick: nick osoby której wypowiedź pasowała
        msg: dopasowana wiadomość
        """
        if not nick in self.conf['admins']:
            mate.say('sorry %s, I don\'t think I can do that' % nick)
            return

        print mate.match

        action = mate.match[0]
        pack_name = mate.match[1]
        modules = mate.match[2].split(' ')[1:]
        if len(modules) == 0:
            modules = None

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
        args = mate.match
        cmd = args[0]
        params = args[1].split(' ')

        print str(mate.match)

        if cmd == u'irccmd':
            n=0
            for s in params:
                if s.startswith(':'):
                    break
                n+=1

            full_cmd = params[:n] + [' '.join(params[n:])[1:]]
            print full_cmd
        elif cmd == u'ctcp':
            full_cmd = ['PRIVMSG', params[0], u'' + chr(1) + ' '.join(params[1:]) + chr(1)]

        print 'IrcCmd: %s: %s' % ( cmd, full_cmd )
        mate.irc.cmd(full_cmd)
