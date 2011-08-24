import code
import logging
from BeautifulSoup import BeautifulSoup
import urllib
import urllib2
import simplejson
import sys


def processPage(url):
    request = urllib2.Request(url)
    request.add_header('User-Agent', 
                       'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.19) '
                       'Gecko/20081202 Firefox (Debian-2.0.0.19-0etch1)')
    opener = urllib2.build_opener(urllib2.HTTPRedirectHandler())
    response = opener.open(request)
    soup = BeautifulSoup(response)

    items = soup.findAll('div', attrs={'id': 'postingTitle'})
    results = { 'data': [] }
    for item in items:
        title = ''.join(item.findAll(text=True)).strip()
        datePosted = item.findNextSiblings('div', attrs={'class': 'adInfo'})[0].text.strip()
        content = ''.join(item.findNextSiblings('div', attrs={'class': 'posting'})[0].div.findAll(text=True)).strip()
        url = ''
        if item.findNextSiblings('div', attrs={'class': 'posting'})[0].find('div', attrs={'class': 'viewAdLink'}):
            url = item.findNextSiblings('div', attrs={'class': 'posting'})[0].find('div', attrs={'class': 'viewAdLink'}).a.get('href')
        images = []
        if len(item.findNextSiblings('div', attrs={'class': 'viewAdLink'})) > 0:
            images = [ k.get('src') for k in item.findNextSiblings('div', attrs={'class': 'viewAdLink'})[0].findAll('img') ]
        results['data'].append({ 'title': title,
                                 'datePosted': datePosted,
                                 'content': content, 
                                 'url': url,
                                 'images': images})
    more = soup.find('a', attrs={'class':'pagination', 'title':'Next'})
    if more:
        more = more.get('href')
    results['more'] = more
    return results

def scrapeBackpage(query, state, max_results):
    params = {'keyword': query, 'layout': 'detailed'}
    url = "http://%s.backpage.com/adult?%s" % (state, urllib.urlencode(params))
    results = []
    while True:
        logging.info("Processing %s." % url)
        new_data = processPage(url)
        results.extend(new_data['data'])
        if new_data['more']:
            url = new_data['more']
        else:
            break
        if max_results > 0 and len(results) > max_results:
            break
    return results

def main(argv):
    logging.basicConfig(level=logging.INFO)
    results = scrapeBackpage('perfect', 'alabama', 50)
    print simplejson.dumps(results, sort_keys=True, indent=2)
    
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main(sys.argv)
    local = {}
    local.update(globals())
    local.update(locals())
    code.interact(local=local)
