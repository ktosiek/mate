# -*- coding: utf-8 -*-
from future_builtins import map, filter

import time
import irc
import pkgutil
import re
import asyncore
import traceback

class ClassWrapper(object):
    def __init__(self, origobj):
        self.myobj = origobj
    def __str__(self):
        return "Wrapped: " + str(self.myobj)
    def __unicode__(self):
        return u"Wrapped: " + unicode(self.myobj)
    def __getattr__(self, attr):
        return getattr(self.myobj, attr)

def noop(*args,**kwargs):
    pass

def run_per_minute(max_runs_per_m, run_if_too_often):
    def decorate(f):
        def run(*args,**kwargs):
            if run.__last_minute == long(time.time())/60:
                run.__runs_last_minute += 1
                if max_runs_per_m >= run.__runs_last_minute:
                    return f(*args, **kwargs)
                else:
                    return run_if_too_often(*args,**kwargs)
            else:
                run.__runs_last_minute = 0
                run.__last_minute = long(time.time())/60
                return f(*args, **kwargs)
        run.__last_minute = time.time()
        run.__runs_last_minute = 0
        return run
    return decorate

class MateModule(object):
    regex = None

    def __init__(self, mate, config):
        self.conf=config

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

        self.irc = irc.IRC(self.conf['server'],
                           self.conf['port'],
                           self.conf['nick'],
                           self.conf['realname'],
                           password = self.conf['password'],
                           use_ssl = self.conf['ssl'],
                           encoding = self.conf['encoding'] )

        self.irc.handlers['PRIVMSG'] = self.irc_privmsg_handler
        self.modules = [] # lista krotek (nazwa_zestawu_modułów, skompilowany regexp, moduł)
        self.load_modules()

    def gen_say_func( self, room ):
        def say( msg ):
            self.msg( room, msg )
        return say

    def gen_reply_func( self, room, nick ):
        def reply( msg ):
            self.msg( room, nick + ': ' + msg )
        return reply

    def irc_privmsg_handler(self, irc, prefix, command, params):
        for m in self.modules:
            match = m[1].match( params[-1] )
            if match != None:
                try:
                    nick = prefix.split('!')[0]
                    msg = params[-1]
                    mate = ClassWrapper( self )
                    mate.say = self.gen_say_func( params[0] )
                    mate.reply = self.gen_reply_func( params[0], nick )
                    mate.match = match
                    
                    m[2].run( mate, nick, msg )
                except BaseException as e:
                    self.gen_say_func( params[0] )( '%s:%s: %s' % \
                                                        (m[0],
                                                         m[2].__class__.__name__,
                                                         str(e).replace('\n', '|')) )

    def msg( self, room, msg ):
        self.irc.msg(room, msg)

    def main(self):
        for chan in self.conf['channels']:
            self.irc.cmd(['JOIN', chan])
        asyncore.loop()

    def load_modules(self):
        """Loads modules from module_paths"""
        for (importer, name, ispkg) in pkgutil.iter_modules( self.conf['module_paths'] ):
            if not name in self.conf['module_blacklist']:
                try:
                    self.load_module_with_importer(importer, name)
                except BaseException as e:
                    print 'Can\'t load %s:\n%s' % (name, e)

    def load_module_with_importer(self, importer, pack_name, load_modules=None):
        print 'Loading modules from %s' % pack_name
        loader = importer.find_module( pack_name )
        module_pack = loader.load_module( pack_name )
        module_names = module_pack.__module_class_names__
        print '  %s' % ', '.join(module_names)
        for module_name in module_names:
            if load_modules == None or module_name in load_modules:
                module = getattr(module_pack, module_name)
                try:
                    print '    %s' % module
                    obj = module(self, self.prepare_module_config( getattr(module_pack, '__module_config__', {})))
                    if obj:
                        m = (pack_name, re.compile(obj.regex), obj)
                        self.modules.append( m )
                        print '       %s' % m[2].regex
                except BaseException as e:
                    print 'Can\'t load %s from %s:\n%s\n' % (module_name, pack_name, e)
                    traceback.print_exc()

    def load_module(self, pack_name, load_modules=None):
        modules = filter( lambda m: m[1] == pack_name,
                          pkgutil.iter_modules( self.conf['module_paths'] ) )
        for (importer, name, ispkg) in modules:
            try:
                self.load_module_with_importer(importer, name, load_modules=load_modules)
            except BaseException as e:
                print 'Can\'t load %s:\n%s' % (name, e)
                traceback.print_exc()

    def unload_module(self, pack_name, module_name=None):
        modules = filter(lambda m: m[0] == pack_name and (module_name == None or m[2].__class__.__name__ == module_name),
                         self.modules)
        for m in modules:
            print 'Unloading %s.%s' % (m[0], m[2])
            m[2].unload()
            self.modules.remove(m)

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
        essentials = ('server', 'port', 'nick', 'realname')
        defaults = (('password', None),
                    ('ssl', False),
                    ('encoding', 'utf8'),
                    ('module_paths', ['modules/']),
                    ('module_blacklist', []),
                    ('channels', []),)

        self.conf = {}

        try:
            for c in essentials:
                self.conf[ c ] = conf[ c ]
        except IndexError as e:
            raise MateConfigException('Missing configuration parameter: %s' % e.args[0])

        for (c, v) in defaults:
            self.conf[ c ] = conf.get(c, v)
