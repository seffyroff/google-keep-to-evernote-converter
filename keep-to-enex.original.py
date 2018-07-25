#!/usr/bin/env python3

import sys
import re
import parsedatetime as pdt
import time

cal = pdt.Calendar()

r1 = re.compile('<div class="listitem checked"><div class="bullet">&#9745;</div>.*?<div class="text">(.*?)</div></div>')
r2 = re.compile('<div class="listitem"><div class="bullet">&#9744;</div>.*?<div class="text">(.*?)</div></div>')
r3 = re.compile('<div class="labels"><span class="label">([^<]*)</span>')

def mungefile(fn):
	fp = open(fn, 'r')
	fp.readline()
	fp.readline()
	title = fp.readline().strip()
	title = title.replace('<title>', '').replace('</title>', '')

	fp.readline()
	fp.readline()
	t = fp.readline()
	tags = ''
	if 'archived' in t:
		tags = '<tag>archived</tag>'
	fp.readline()
	date = fp.readline().strip().replace('</div>', '')
	dt, flat = cal.parse(date)
	iso = time.strftime('%Y%m%dT%H%M%SZ',
						time.gmtime(time.mktime(dt)))

	extratitle = fp.readline()
	content = fp.readline().replace('<div class="content">', '')

	for line in fp:
		line = line.strip()
		if line == '</div></body></html>':
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

	m = r3.search(content)
	if m:
		content = content[:m.start()]
		tags = '<tag>' + m.group(1) + '</tag>'

	content = content.replace('\0', '\n')

	# remove final div close
	content = content.strip()
	if content.endswith('</div>'):
		content = content[:-6]

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
<en-export export-date="20180502T065115Z" application="Evernote" version="Evernote Mac 6.10 (454269)">''')
for arg in sys.argv[1:]:
	mungefile(arg)
print ('''</en-export>''')
