# -*- coding: utf-8 -*-
__module_class_names__ = ["Title"]

from mate import MateModule, run_per_minute, run_in_background, noop
import urllib.request, urllib.error, urllib.parse
import re
import htmllib

def unescape(s):
    p = htmllib.HTMLParser(None)
    p.save_bgn()
    p.feed(s)
    return p.save_end()

class Title(MateModule):
    def __init__(self, mate, config):
        MateModule.__init__(self, mate, config)
        self.regex = '(https?://((([a-zA-Z0-9]+\.)+[a-zA-Z]{2,3}(:[0-9]+)?)|([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+))(/[^ ]*)*)'
        self.conf['threadable'] = True
        self.conf['thread_timeout'] = 10.0

    @run_per_minute(30, noop)
    def run(self, mate, nick, msg):
        threads = []
        for url in [ m[0] for m in mate.all_matches ]:
            #threads += self.check_title( url, mate )
            if re.match('^https?://(192\.168\.[0-9]+\.[0-9]+|10\.0\.[0-9]+\.[0-9]+|127\.0\.0\.[0-9]+)', url):
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
