#!/usr/bin/env python3

# originally created and posted by user dgc on
# https://discussion.evernote.com/topic/97201-how-to-transfer-all-the-notes-from-google-keep-to-evernote/

# until now, Google Takeout for Keep does NOT export:
# - correct order of lists notes (non-checked first, checked last)
# - list items indentation

import sys
import re
import parsedatetime as pdt
import time

cal = pdt.Calendar()

r1 = re.compile('<li class="listitem checked"><span class="bullet">&#9745;</span>.*?<span class="text">(.*?)</span>.*?</li>')
r2 = re.compile('<li class="listitem"><span class="bullet">&#9744;</span>.*?<span class="text">(.*?)</span>.*?</li>')
r3 = re.compile('<span class="chip label"><span class="label-name">([^<]*)</span>[^<]*</span>')


def readlineUntil(file, str):
        currLine = ""
        while not str in currLine:
                currLine = file.readline()
        return currLine

def mungefile(fn):
        fp = open(fn, 'r')
        
        #title = fp.readline().strip()
        title = readlineUntil( fp, "<title>" ).strip()
        title = title.replace('<title>', '').replace('</title>', '')

        readlineUntil( fp, "<body>" )
        t = fp.readline()
        tags = ''
        if '"archived"' in t:
                tags = '<tag>archived</tag>'
        fp.readline() #</div> alone

        date = fp.readline().strip().replace('</div>', '')
        dt, flat = cal.parse(date)
        iso = time.strftime('%Y%m%dT%H%M%SZ', time.gmtime(time.mktime(dt)))

        fp.readline()  # extra title

        # I still couldn't import a note with an image attachment
        # MAYBE I could turn this replace into a standard div
        # and remove the div removal below... just an idea.
        # For the moment, I'll just import the offending note by hand,
        # but if you have lots of notes with attached images, this code
        # still doesn't handle it
        content = fp.readline().replace('<div class="content">', '')
        content = content.replace( '<ul class="list">', '' )

        for line in fp:
                line = line.strip()
                if line == '</div></body></html>' or line.startswith('<div class="chips">'):
                        break
                content += line + '\n'

        content = content.replace('<br>', '<br/>')
        content = content.replace('\n', '\0')

        while True:
                m = r1.search(content)
                if not m:
                        break
                content = content[:m.start()] + '<en-todo checked="true"/>' + m.group(1) + '<br/>' + content[m.end():]

        while True:
                m = r2.search(content)
                if not m:
                        break
                content = content[:m.start()] + '<en-todo checked="false"/>' + m.group(1) + '<br/>' + content[m.end():]

        content = content.replace('\0', '\n')

        # remove final div close
        content = content.strip()
        if content.endswith('</div>'):
                content = content[:-6]
        # remove list close (if it was a list)
        if content.endswith('</ul>'):
                content = content[:-5]


        #line might still has chips
        if line.startswith('<div class="chips">'):
                content += line + '\n'
        for line in fp:
                line = line.strip()
                if line == '</div></body></html>':
                        break
                content += line + '\n'

        m = r3.search(content)
        if m:
                content = content[:m.start()] + content[m.end():]
                tags = '<tag>' + m.group(1) + '</tag>'

        content = re.sub(
                r'class="[^"]*"',
                '',
                content
        )


        fp.close()
                
        print ('''
  <note>
    <title>{title}</title>
    <content><![CDATA[<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd"><en-note style="word-wrap: break-word; -webkit-nbsp-mode: space; -webkit-line-break: after-white-space;">{content}</en-note>]]></content>
    <created>{iso}</created>
    <updated>{iso}</updated>
    {tags}
    <note-attributes>
      <latitude>0</latitude>
      <longitude>0</longitude>
      <source>google-keep</source>
      <reminder-order>0</reminder-order>
    </note-attributes>
  </note>
'''.format(**locals()))

print ('''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE en-export SYSTEM "http://xml.evernote.com/pub/evernote-export3.dtd">
<en-export export-date="20180502T065115Z" application="Evernote/Windows" version="6.x">''')
for arg in sys.argv[1:]:
        mungefile(arg)
print ('''</en-export>''')
