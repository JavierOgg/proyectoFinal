#!/usr/bin/env python
# -*- coding: utf-8 -*-
#from web import run, background, backgrounder
import web
from datetime import datetime
from time import sleep
from background import background, backgrounder

now = datetime.now
urls = (
    '/', 'index',
)

web.config.debug = True
app = web.application(urls, globals())
app.internalerror = web.debugerror

form_main = """$def with (o)
<HTML>
<HEAD>
    <STYLE>
        @import '/static/skin/default.css';
    </STYLE>
</HEAD>
<BODY>
<CENTER>
<H3>Background runner</H3>
<P/>
<P/>
<IFRAME src='/static/out.html' width='50%' height='70%'>
</IFRAME>
</BODY>
</HTML>
"""


class index:
    def GET(self):
        o = web.Storage
        self.startthread()
        t = web.template.Template(form_main)
        return t(o)

    @backgrounder
    def startthread(self):
        longrunning()


@background
def longrunning():

    open('./static/out.html', 'wt').write("""<HTML><HEAD>
<META HTTP-EQUIV=Pragma CONTENT=no-cache>
<META HTTP-EQUIV=Refresh CONTENT=1>
</HEAD><BODY>Background thread is running...<BR>""")
    for i in range(10):
        sleep(3)
        open('./static/out.html', 'at').write("%s: %s<BR>" % (i, now()))

if __name__ == '__main__':
    app.run()
