# -*- coding: utf-8 -*-
from mate import MateModule
import logging

log = logging.getLogger('Admin')

__module_class_names__ = ["Reload", "IrcCmd", "JoinPart", "Say"]
__module_config__ = { 'admins': (['tomekk'],
                                 list,
                                 """ List of administrators """),
                      }

def admins_only(f):
    def run(module, mate, nick, msg):
        if not nick in module.conf['admins']:
            mate.say('sorry %s, I don\'t think I can do that' % nick)
        else:
            return f(module, mate, nick, msg)
    return run

class Reload(MateModule):
    def __init__(self, mate, config):
        MateModule.__init__(self, mate, config)
        self.regex = mate.conf['nick'] + ': (reload|unload) ([a-zA-Z0-9_]*)(( ([a-zA-Z0-9]+))*)'

    @admins_only
    def run(self, mate, nick, msg):
        """
        mate: instancja Mate
        nick: nick osoby której wypowiedź pasowała
        msg: dopasowana wiadomość
        """

        action = mate.match[0]
        pack_name = mate.match[1]
        modules = mate.match[2].split(' ')[1:]
        if len(modules) == 0:
            modules = None

        mate.unload_module( pack_name, modules )
        if action == 'reload':
            mate.load_module( pack_name, modules )
            mate.reply( 'Done.' )
        else:
            mate.reply( 'Done.' )

class IrcCmd(MateModule):
    def __init__(self, mate, config):
        MateModule.__init__(self, mate, config)
        self.regex = mate.conf['nick'] + ': (irccmd|ctcp) (.*)'

    @admins_only
    def run(self, mate, nick, msg):
        if not nick in self.conf['admins']:
            mate.say('sorry %s, I don\'t think I can do that' % nick)
            return

        args = mate.match
        cmd = args[0]
        params = args[1].split(' ')

        if cmd == 'irccmd':
            n=0
            for s in params:
                if s.startswith(':'):
                    break
                n+=1

            full_cmd = params[:n] + [' '.join(params[n:])[1:]]
        elif cmd == 'ctcp':
            full_cmd = ['PRIVMSG', params[0], '' + chr(1) + ' '.join(params[1:]) + chr(1)]

        log.info('|' + str(full_cmd))
        mate.irc.cmd(full_cmd)

class JoinPart(MateModule):
    def __init__(self, mate, config):
        MateModule.__init__(self, mate, config)
        self.regex = '^' + mate.conf['nick'] + ': (join|part) ([^ ]+) *$'

    @admins_only
    def run(self, mate, nick, msg):
        cmd = mate.match[0].upper()
        channel = mate.match[1]
        log.info( '|%s %s' % (cmd, channel) )
        if cmd == 'JOIN':
            mate.irc.cmd( [ cmd, channel ] )

class Say(MateModule):
    def __init__(self, mate, config):
        MateModule.__init__(self, mate, config)
        self.regex = '^' + mate.conf['nick'] + ': say ([^ ]+) (.*)'

    @admins_only
    def run(self, mate, nick, msg):
        mate.msg( mate.match[0], mate.match[1] )
