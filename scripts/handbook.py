# -*- coding: utf-8 -*-

import re
import sys
from csv import DictReader

def extract_keywords(title):
    """Extracts keywords from a title, and returns the title and a dictionary of keys and values"""
    dict = {}
    print("Starting with {}".format(title))
    for key, value in re.findall('%(\w+) ([^%]+)', title):
        print("Found {} -> {} in [{}]".format(key, value, title))
        dict[key] = value

    if title.find('%') != -1:
        title = title[:title.find('%')].strip()

    print("Extract keywords returning {} -> {}".format(title, dict))
    return title, dict
        
def latex_escape(str):
    """Replaces unescaped special characters with escaped versions, and does
    other special character conversions."""
    
    str = str.replace('~','{\\textasciitilde}')
#    str = str.replace('β','\\beta')

    # escape these characters if not already escaped
    special_chars = r'\#\@\&\$\_\%'
    patternstr = r'([^\\])([%s])' % (special_chars)
    str = re.sub(patternstr, '\\1\\\\\\2', str)

    # fix superscripts
#    str = re.sub(r'([^$])\^(.*?) ', r'\1$^\2$ ',  str)
    return str

class Paper:
    def __init__(self, line, subconf):
        self.id, rest = line.split(' ', 1)
        if re.match(r'^\d+', rest) is not None:
            self.time, comment = rest.split(' ', 1)
            self.poster = False
        else:
            self.time = None
            self.poster = True
            comment = rest

        if self.id.find('/') != -1:
            tokens = self.id.split('/')
            self.id = '%s-%s' % (tokens[1].lower(), threedigits(tokens[0]))
        else:
            self.id = '%s-%s' % (subconf, threedigits(self.id))
            
    def __str__(self):
        return "%s %s" % (self.id, self.time)

def threedigits(str):
    return '%03d' % (int(str))

class Session:
    def __init__(self, line, date):
        # remove comments
        if line.find('#') > 0:
            line = line[:line.find('#')]
        (self.time, namestr) = line[2:].split(' ', 1)
        self.date = date
        self.papers = []
        self.desc = ""
        
        (self.name, self.keywords) = extract_keywords(namestr)
        
        if self.name.find(':') != -1:
            colonpos = self.name.find(':')
            self.desc = self.name[colonpos+2:]
            self.name = self.name[:colonpos]
            print ("Looking for num in name ["+self.name+"], desc ["+self.desc+"]")
            self.num = self.name.split(' ')[-1][:-1]
            print("Got "+self.num)
            self.track = self.name.split(' ')[-1][-1]
            print >> sys.stderr, "LINE %s NAME %s DESC %s NUM %s TRACK %s" % (line, self.name, self.desc, self.num, self.track)
        else:
            print >> sys.stderr, "LINE %s NAME %s" % (line, self.name)

        self.poster = self.track is not None and self.track >= "P"
        # l = self.name.lower()
        # if 'poster' in l or 'demo' in l or 'best paper' in l:
        #     self.poster = True

    def __str__(self):
        return "SESSION [%s/%s] %s %s %s" % (self.date, self.time, self.name, self.desc, self.keywords)

    def add_paper(self,paper):
        self.papers.append(paper)

    def chair(self):
        """Returns the (first name, last name) of the chair, if found in a %chair keyword"""
        
        if self.keywords.has_key('chair'):
            fullname = self.keywords['chair']
            if ',' in fullname:
                names = fullname.split(', ')
                return (names[1].strip(), names[0].strip())
            else:
                # This is just a heuristic, assuming the first name is one word and the last
                # name is 1+ words
                names = fullname.split(' ', 1)
                return (names[0].strip(), names[1].strip())
        else:
            return ('', '')

