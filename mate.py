# -*- coding: utf-8 -*-
import logging
import time
import irc
import pkgutil
import re
import asyncore
import traceback
import socket # dla socket.error
from threading import Timer
from threading2 import Thread

log = logging.getLogger('Mate')

class ClassWrapper(object):
    def __init__(self, origobj):
        self.myobj = origobj
    def __str__(self):
        return "Wrapped: " + str(self.myobj)
    def __unicode__(self):
        return "Wrapped: " + str(self.myobj)
    def __getattr__(self, attr):
        return getattr(self.myobj, attr)

def noop(*args,**kwargs):
    pass

def run_per_minute(max_runs_per_m, run_if_too_often):
    def decorate(f):
        def run(*args,**kwargs):
            if run.__last_minute == int(time.time())/60:
                run.__runs_last_minute += 1
                if max_runs_per_m >= run.__runs_last_minute:
                    return f(*args, **kwargs)
                else:
                    return run_if_too_often(*args,**kwargs)
            else:
                run.__runs_last_minute = 0
                run.__last_minute = int(time.time())/60
                return f(*args, **kwargs)
        run.__last_minute = time.time()
        run.__runs_last_minute = 0
        return run
    return decorate

def run_in_background(timeout=None):
    def decorate(f):
        def run(*args, **kwargs):
            timer = False
            def f_and_timer(*args, **kwargs):
                f(*args, **kwargs)
                timer and timer.cancel()

            log.debug( 'starting bg thread with timeout %s', timeout )
            thread = Thread( target = f_and_timer, args=args, kwargs=kwargs )

            def stop():
                log.debug( 'stopping thread %s', thread )
                thread.terminate()

            if timeout != None:
                timer = Timer(timeout, stop)
                timer.start()

            thread.start()
            return thread
            
        return run
    return decorate

class MateModule(object):
    regex = None

    def __init__(self, mate, config):
        self.conf=config
        self.conf['threadable'] = config.get('threadable', False)
        if self.conf['threadable']:
            self.conf['thread_timeout'] = config.get('thread_timeout', 5.0)

    def run(self, mate, nick, msg):
        """
        mate: instancja Mate
        nick: nick osoby której wypowiedź pasowała
        msg: dopasowana wiadomość
        """
        pass

    def unload(self):
        pass

class MateConfigException(Exception):
    pass

class Mate(object):
    def __init__(self, config):
        self.set_config( config )
        self.modules = [] # lista krotek (nazwa_zestawu_modułów, skompilowany regexp, moduł)
        self.load_modules()

    def connect(self):
        log.info('Connecting to %(server)s:%(port)s as %(nick)s (%(realname)s)' % self.conf)
        self.irc = irc.IRC(self.conf['server'],
                           self.conf['port'],
                           self.conf['nick'],
                           self.conf['realname'],
                           password = self.conf['password'],
                           use_ssl = self.conf['ssl'],
                           encoding = self.conf['encoding'] )

        self.irc.handlers['PRIVMSG'] = self.irc_privmsg_handler
        self.irc.handlers['KICK'] = self.irc_kick_handler
        self.irc.handlers['NOTICE'] = self.irc_notice_handler

    def gen_say_func( self, room ):
        def say( msg ):
            self.msg( room, msg )
        return say

    def gen_reply_func( self, room, nick ):
        def reply( msg ):
            self.msg( room, nick + ': ' + msg )
        return reply

    def irc_notice_handler(self, irc, prefix, command, params):
        for m in self.modules:
            if hasattr(m, 'notice_handler'):
                m.notice_handler(params)

    def irc_privmsg_handler(self, irc, prefix, command, params):
        nick = prefix.split('!')[0]
        msg = params[-1]
        channel = params[0]
        mate = ClassWrapper( self )
        mate.say = self.gen_say_func( channel )
        mate.reply = self.gen_reply_func( channel, nick )

        log.info( '%s|< %s>%s', channel, nick, msg)
        for m in self.modules:
            for msg in [ msg, ''.join(reversed(msg)) ]:
                all_matches = m[1].findall( msg )
                if len(all_matches) > 0:
                    try:
                        mate.match = all_matches[0]
                        mate.all_matches = all_matches

                        log.debug( '%s: %s', m[2].__class__.__name__, all_matches )
                        
                        if m[2].conf['threadable']:
                            run_in_background( m[2].conf['thread_timeout'] )(m[2].run)( mate, nick, msg )
                        else:
                            m[2].run( mate, nick, msg )
                    except BaseException as e:
                        self.gen_say_func( channel )( '%s:%s: %s' % \
                                                            (m[0],
                                                             m[2].__class__.__name__,
                                                             str(e).replace('\n', '|')) )
                        log.debug( 'Exception: ', exc_info=1 )

    def irc_kick_handler(self, irc, prefix, command, params):
        if self.conf['autorejoin']:
            self.irc.cmd(['JOIN', params[0]])

    def msg( self, room, msg ):
        log.info( '%s|<> %s', room, msg )
        self.irc.msg(room, msg)

    def main(self):
        while True: # asyncore skończy się razem z zerwaniem połączenia
            try:
                self.connect()
                for chan in self.conf['channels']:
                    self.irc.cmd(['JOIN', chan])
                asyncore.loop()
            except socket.error as exc:
                log.error('Problem connecting: %(errno)s: %(strerror)s' % {
                    'errno': exc.errno,
                    'strerror': exc.strerror, } )
            time.sleep(4)

    def load_modules(self):
        """Loads modules from module_paths"""
        for (importer, name, ispkg) in pkgutil.iter_modules( self.conf['module_paths'] ):
            if not name in self.conf['module_blacklist']:
                try:
                    self.load_module_with_importer(importer, name)
                except BaseException as e:
                    log.error( 'Can\'t load %s', name )
                    log.debug( 'Exception:', exc_info=1 )

    def load_module_with_importer(self, importer, pack_name, load_modules=None):
        log.info('Loading modules from %s', pack_name)
        loader = importer.find_module( pack_name )
        module_pack = loader.load_module( pack_name )
        module_names = module_pack.__module_class_names__
        log.info('  %s', ', '.join(module_names))
        for module_name in module_names:
            if load_modules == None or module_name in load_modules:
                module = getattr(module_pack, module_name)
                try:
                    log.debug('    %s', module)
                    obj = module(self, self.prepare_module_config( getattr(module_pack, '__module_config__', {})))
                    if obj:
                        m = (pack_name, re.compile(obj.regex), obj)
                        self.modules.append( m )
                        log.debug( '       %s', m[2].regex )
                except BaseException as e:
                    log.error( 'Can\'t load %s from %s', module_name, pack_name, e)
                    log.debug( 'Exception: ', exc_info=1)

    def load_module(self, pack_name, load_modules=None):
        modules = filter( lambda m: m[1] == pack_name,
                          pkgutil.iter_modules( self.conf['module_paths'] ) )
        for (importer, name, ispkg) in modules:
            try:
                self.load_module_with_importer(importer, name, load_modules=load_modules)
            except BaseException as e:
                log.error( 'Can\'t load %s:\n%s', name, e )
                log.debug( 'Exception: ', exc_info=1 )

    def unload_module(self, pack_name, module_names=None):
        log.info( 'Trying to unload %s from %s', ', '.join(module_names or []), pack_name )
        
        remove_me = []
        for m in self.modules:
            if m[0] == pack_name:
                if (module_names == None) or (m[2].__class__.__name__ in module_names):
                    remove_me.append( m )

        for m in remove_me:
            self.modules.remove(m)
            m[2].unload()
            log.info( 'Unloading %s.%s', m[0], m[2] )

    def prepare_module_config(self, config):
        prepared = {}
        for key in config:
            if not isinstance(config[key][0], config[key][1]):
                raise MateConfigException('config option %s needs %s, but %s given' % \
                                              (key, config[key][1], config[key][0]))
            else:
                prepared[key] = config[key][0]
        return prepared

    def set_config(self, conf):
        essentials = ('server', 'port', 'nick', 'realname', 'owner')
        defaults = (('password', None),
                    ('ssl', False),
                    ('encoding', 'utf8'),
                    ('module_paths', ['modules/']),
                    ('module_blacklist', []),
                    ('channels', []),
                    ('autorejoin', True),)

        self.conf = {}

        try:
            for c in essentials:
                self.conf[ c ] = conf[ c ]
        except IndexError as e:
            raise MateConfigException('Missing configuration parameter: %s' % e.args[0])

        for (c, v) in defaults:
            self.conf[ c ] = conf.get(c, v)
