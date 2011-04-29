# -*- coding: utf-8 -*-
__module_class_names__ = ["Title"]

from mate import MateModule, run_per_minute, run_in_background, noop
import urllib.request, urllib.error, urllib.parse
import re

html_unescape_table = {
    "&amp;":"&",
    "&quot;":'"',
    "&apos;":"'",
    "&gt;":">",
    "&lt;":"<",
    }

def unescape(text):
    for p in html_unescape_table:
        text = text.replace( p, html_unescape_table[p] )
    return text

class Title(MateModule):
    def __init__(self, mate, config):
        MateModule.__init__(self, mate, config)

        domain_name = '([^.]+\.)+[a-zA-Z]{2,}'
        ipv4 = '[0-9.]+' # taaa, akurat. Ale wystarczy. podobnie z ipv6
        ipv6 = '[0-9a-fA-F:]+'
        protocols = 'https?'
        port = '[0-9]+'

        self.regex = '(' + protocols + '://(' + '|'.join( (domain_name, ipv4, ipv6) ) + ')(:' + port + ')?(/[^ ]*)*)'
        self.conf['threadable'] = True
        self.conf['thread_timeout'] = 10.0

    @run_per_minute(30, noop)
    def run(self, mate, nick, msg):
        threads = []
        for m in mate.all_matches:
            url = m[0]
            host = m[1]
            #threads += self.check_title( url, mate )
            if host.startswith('192.168.') or host.startswith('10.') or host.startswith('127.') or host == 'localhost' or host.endswith('.lan'):
                return
            self.check_title( url, mate )

#        for t in threads:
#            if t.isActive():
#                t.join()

    @run_in_background(10.0)
    def check_title(self, url, mate):
        f = urllib.request.urlopen( url, None, 8.0 )
        buf = f.read(4096)
        encoding = 'utf8'
        try:
            encoding = re.findall( '<meta http-equiv="Content-Type" content="text/html; charset=([a-zA-Z0-9-]*)">',
                                   buf.decode('ascii', 'replace') )[0].lower()
            if encoding == 'utf-8':
                encoding = 'utf8'
        except (UnicodeDecodeError, IndexError):
            pass
        buf = buf.decode(encoding, 'replace')
        title = re.findall('(?mi)<title>(.*)</title>', buf.replace('\n','').replace('\r',''))
        if len(title) > 0:
            mate.say( url + '  => ' + unescape(title[0]) )
