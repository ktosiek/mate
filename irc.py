from future_builtins import map, filter

import asynchat
import socket
import ssl
import re

class IRC(asynchat.async_chat):
    reply_names = { '001': 'RPL_WELCOME',
                    #    "Welcome to the Internet Relay Network <nick>!<user>@<host>"
                    '002': 'RPL_YOURHOST',
                    #    "Your host is <servername>, running version <ver>"
                    '003': 'RPL_CREATED',
                    #    "This server was created <date>"
                    '004': 'RPL_MYINFO',
                    #    "<servername> <version> <available user modes> <available channel modes>"
                    '005': 'RPL_BOUNCE',
                    #    "Try server <server name>, port <port number>"
                    '251': 'RPL_LUSERCLIENT',
                    #    ":There are <integer> users and <integer> services on <integer> servers"
                    '252': 'RPL_LUSEROP',
                    #    "<integer> :operator(s) online"
                    '253': 'RPL_LUSERUNKNOWN',
                    #    "<integer> :unknown connection(s)"
                    '254': 'RPL_LUSERCHANNELS',
                    #    "<integer> :channels formed"
                    '255': 'RPL_LUSERME',
                    #":I have <integer> clients and <integer> servers"
                    '375': 'RPL_MOTDSTART',
                    #    ":- <server> Message of the day - "
                    '372': 'RPL_MOTD',
                    #    ":- <text>"
                    '376': 'RPL_ENDOFMOTD',
                    #    ":End of MOTD command"
                    '331': 'RPL_NOTOPIC',
                    #    "<channel> :No topic is set"
                    '332': 'RPL_TOPIC',
                    #    "<channel> :<topic>"
                    '353': 'RPL_NAMREPLY',
                    #    "( "=" / "*" / "@" ) <channel>
                    #    :[ "@" / "+" ] <nick> *( " " [ "@" / "+" ] <nick> )
                    # - "@" is used for secret channels, "*" for private channels, and "=" for others (public channels).
                    '366': 'RPL_ENDOFNAMES',
                    #    "<channel> :End of NAMES list"

                    }

    def __init__(self, server, port, nick, realname, password=None, use_ssl=False, encoding='utf8'):
        self.addr = (server, port)
        self.encoding = encoding

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect( self.addr )
        if use_ssl:
            sock = ssl.wrap_socket(sock)

        asynchat.async_chat.__init__(self, sock=sock )

        self.nick = nick
        self.realname = realname
        self.ibuffer = []
        self.set_terminator("\r\n")
        self.handlers = {}

        if password != None:
            self.cmd(['PASS', password])
        self.cmd(['NICK', self.nick])
        self.cmd(['USER', self.nick, 0, '*', self.realname])

        self.handlers['PING'] = IRC.ping_handler

    def collect_incoming_data(self, data):
        self.ibuffer.append(data)

    def ping_handler(self, prefix, command, params):
        self.cmd(['PONG'] + params)

    def found_terminator(self):
        def irc_split(s):
            (prefix, command, params) = re.match(r"""(:[^ ]* |)([a-zA-Z]+|[0-9]{3})(.*)""", s).groups()
            if len(prefix) > 0:
                prefix = prefix[1:-1] # deleting ':' from the front and ' ' from the end

            command = IRC.reply_names.get( command, command )

            params = params.split(' :') # for the last parameter, the only one that can contain spaces
            params = params[0].split(' ')[1:] + [ ' :'.join(params[1:]) ]

            return (prefix, command, params)

        (prefix, command, params) = irc_split(''.join(self.ibuffer).decode(self.encoding))
        self.handlers.get( command, IRC.unhandled_reply_warning)(self, prefix, command, params)
        self.ibuffer = []

    def unhandled_reply_warning(self, prefix, command, params):
            print 'UNHANDLED REPLY:' + unicode(prefix) + ' ' + unicode(command) + ' ' + unicode(params)

    def msg(self, chan, msg):
        self.cmd(['PRIVMSG', chan, msg])

    def cmd(self, msg):
        message = ' '.join( list(map(lambda s: unicode(s).replace(' ',''), msg[:-1]))
                            + [u':' + unicode(msg[-1])] )

        message += "\r\n"

        self.push(bytearray(message.encode(self.encoding,'replace')))

    def upper(string):
        return reduce( lambda s,r: s.replace(*r),
                       (('{','['), ('}',']'), ('\\','|'), ('^','~')),
                       string.upper() )

    def lower(string):
        return reduce( lambda s,r: s.replace(*r),
                       (('[','{'), (']','}'), ('|','\\'), ('~','^')),
                       string.lower() )
