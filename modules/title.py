# -*- coding: utf-8 -*-
__module_class_names__ = ["Title"]

from mate import MateModule, run_per_minute, run_in_background, noop
import urllib2
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
        self.regex = u'(https?://([a-zA-Z0-9]+\.)+[a-zA-Z]{2,3}(:[0-9]+)?(/[^ ]*)*)'
        self.conf['threadable'] = True
        self.conf['thread_timeout'] = 10.0

    @run_per_minute(30, noop)
    def run(self, mate, nick, msg):
        threads = []
        for url in [ m[0] for m in mate.all_matches ]:
            #threads += self.check_title( url, mate )
            self.check_title( url, mate )

#        for t in threads:
#            if t.isActive():
#                t.join()

    @run_in_background(10.0)
    def check_title(self, url, mate):
        f = urllib2.urlopen( url, None, 8.0 )
        buf = f.read(4096)
        try:
            encoding = 'utf8'
            encoding = re.findall( '<meta http-equiv="Content-Type" content="text/html; charset=([a-zA-Z0-9-]*)">',
                                   buf )[0].lower()
            if encoding == 'utf-8':
                encoding = 'utf8'
            buf = buf.decode( encoding )
        except (UnicodeDecodeError, IndexError):
            buf = buf.decode('ascii', 'replace')
        title = re.findall('(?mi)<title>(.*)</title>', buf.replace('\n','').replace('\r',''))
        if len(title) > 0:
            mate.say( url + ': ' + unescape(title[0]) )
