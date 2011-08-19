#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

import urllib2
import urllib
from BeautifulSoup import BeautifulSoup
import simplejson
import logging

def scrapeGoogle(query, site, start):
    entity = urllib.quote(query)
    site_restrict = urllib.quote('site:%s' % site)
    URL = "http://www.google.com/search?q=%s+%s&start=%d" % (entity, site_restrict, start)
    
    logging.info("Processing %s" % URL)
    results = []
    request = urllib2.Request(URL)
    request.add_header('User-Agent', 
                       'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.19) '
                       'Gecko/20081202 Firefox (Debian-2.0.0.19-0etch1)')
    opener = urllib2.build_opener(urllib2.HTTPRedirectHandler())
    response = opener.open(request)
    soup = BeautifulSoup(response)
    results.extend([ {'item': ''.join(k.findAll(text=True)), 'url': k['href']} for k in soup.findAll('a', attrs={'class': 'l'})])
    return results

class MainHandler(webapp.RequestHandler):
    def get(self):
        query = self.request.get('query')
        site = self.request.get('site')
        start = self.request.get('start', '0')
        data = simplejson.dumps(scrapeGoogle(query, site, int(start)))
        if self.request.get('callback'):
            data = "%s(%s)" % (self.request.get('callback'), data)
        self.response.out.write(data)

def main():
    application = webapp.WSGIApplication([('/', MainHandler)],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
