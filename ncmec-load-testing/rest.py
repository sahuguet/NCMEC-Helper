import urllib
import urllib2
import MultipartPostHandler
import code
import logging
import sys
import libxml2
from cStringIO import StringIO
import messages
import socket

timeout = 20
socket.setdefaulttimeout(timeout)

NCMEC_URL = 'http://exttest.cybertip.org/ispws'
NCMEC_SUBMIT = 'http://exttest.cybertip.org/ispws/submit'
NCMEC_UPLOAD= 'http://exttest.cybertip.org/ispws/upload'
NCMEC_FILEINFO = 'http://exttest.cybertip.org/ispws/fileinfo'
NCMEC_FINISH = 'http://exttest.cybertip.org/ispws/finish'


# The data to be extracted from the response XML message.
NCMEC_RESPONSE = {
    'submitResponse': { 'responseCode': '//responseCode',
                        'reportId': '//reportId' },
    'uploadResponse': { 'responseCode': '//responseCode',
                        'reportId': '//reportId',
                        'fileId': '//fileId' },
    'fileDetailsResponse': { 'responseCode': '//responseCode',
                             'reportId': '//responseId',
                             'fileId': '//fileId' },
    'finishResponse': { 'reportId': '//reportId',
                        'fileId': '//fileId' }
    }

USERNAME=''
PASSWORD=''

# create a password manager and install it
password_manager = urllib2.HTTPPasswordMgrWithDefaultRealm()
password_manager.add_password(None,
                              NCMEC_URL,
                              USERNAME,
                              PASSWORD)
handler = urllib2.HTTPBasicAuthHandler(password_manager)
opener = urllib2.build_opener(handler, MultipartPostHandler.MultipartPostHandler)
urllib2.install_opener(opener)

def __getResponseData(response, values):
    try:
        tree = libxml2.parseDoc(response)
        data = {}
        for k, v in values.items():
            data[k] = '|'.join(map(str, tree.xpathEval(v+"/text()")))
        return data
    except Exception, e:
        logging.error(e)
        logging.error(response)
        return { 'responseCode': '-1' }

def __submitData(url, data, isXML=True):
    try:
        logging.debug('Submitting some data')
        logging.debug(data)
        req = urllib2.Request(url, data)
        if isXML == True:
            req.add_header('Content-Type', 'application/xml')
        response = urllib2.urlopen(req)
        logging.debug('We got the response back.')
        return response.read()
    except Exception, e:
        logging.error(e)
        return None

def submitReport(incident_type, url, reporting_person):
    logging.debug('Submitting a report.')
    data = messages.__createReport(incident_type, url, reporting_person)
    response = __submitData(NCMEC_SUBMIT, data)
    if response:
        return __getResponseData(response, NCMEC_RESPONSE['submitResponse'])
    else:
        return { 'responseCode': '-1' }

def uploadFile(report_id, filename):
    logging.debug('Uploading a file.')
    data = { 'id': str(report_id),
             'file': open(filename) }
    try:
      response = urllib2.urlopen(NCMEC_UPLOAD, data)
      raw = response.read()
      logging.debug(raw)
      return (__getResponseData(raw, NCMEC_RESPONSE['uploadResponse']), raw)
    except Exception, e:
      logging.error(e)
      return ( {'responseCode': '-1'}, None)

__some_details =  [ { 'type': 'EXIF',
                      'data': [ { 'name': 'lat', 'value': '123.45' },
                                { 'name': 'lng', 'value': '-123.45' }] },
                    ]

def submitFileDetails(report_id, file_id, filename, details):
    logging.debug('Submitting file details.')
    data = messages. __createFileDetails(report_id, file_id, filename, details)
    logging.debug(data)
    raw = __submitData( NCMEC_FILEINFO, data)
    return (__getResponseData(raw, NCMEC_RESPONSE['fileDetailsResponse']), raw)

def submitFinish(report_id):
    logging.debug('Closing the report.')
    response = __submitData(NCMEC_FINISH, urllib.urlencode( { 'id': report_id } ), False)
    logging.debug(response)
    return __getResponseData(response, NCMEC_RESPONSE['finishResponse'])
                             
  
INCIDENT_TYPE = ['Child Pornography (possession, manufacture, and distribution)', 'Child Prostitution', 'Child Sex Tourism', 'Child Sexual Molestation (not by family member)', 'Misleading Domain Name', 'Misleading Words or Digital Images on the Internet', 'Online Enticement of Children for Sexual Acts', 'Unsolicited Obscene Material Sent to a Child']

def getRandomIncidentType():
  return INCIDENT_TYPE[0]

def session_v1(submitDetails=True):
    file_ids = []
    resp = submitReport(getRandomIncidentType(),
                        'http://goo.gl', { 'first_name': 'Arnaud',
                                           'last_name': 'Sahuguet',
                                           'email': 'sahuguet@google.com'})
    if resp['responseCode'] != '0':
      logging.error("Failed to submit report.")
      return (-1, 'Failed to submit report');

    reportId = resp['reportId']
   
    (resp, raw) = uploadFile(reportId, 'the_image.jpg')
    if resp['responseCode'] != '0':
        logging.error('Failed to upload file.')
        logging.error(resp)
        logging.error(raw)
        return (-1, 'Failed to upload file')
    fileId = resp['fileId']
    if resp['reportId'] != reportId:
        return (-1, 'reportId not matching')
    file_ids.append(fileId)

    if submitDetails:
        (resp, raw) = submitFileDetails(reportId, fileId, 'the_image.jpg', __some_details)
        logging.debug(raw, resp)
        if resp['responseCode'] != '0':
            logging.error('Failed to submit file details.')
            return (-1, 'Failed to submit file details')
    
    (resp, raw) = uploadFile(reportId, 'the_image2.jpg')
    if resp['responseCode'] != '0':
        logging.error('Failed to upload file.')
        logging.error(resp)
        logging.error(raw)
        return (-1, 'Failed to upload file')
    fileId = resp['fileId']
    if resp['reportId'] != reportId:
        return (-1, 'reportId not matching')
    file_ids.append(fileId)
    
    resp = submitFinish(reportId)
    __files = resp['fileId']
    number_of_files = len(__files.split('|'))
    if number_of_files != len(file_ids):
        logging.error(file_ids)
        logging.error(__files)
        return (-1, 'Wrong number of files')
    return (0, 'OK')

def main(argv):
    resp = submitReport(getRandomIncidentType(),
                        'http://goo.gl', { 'first_name': 'Arnaud',
                                           'last_name': 'Sahuguet',
                                           'email': 'sahuguet@google.com'})
    print resp
    reportId = resp['reportId']
    resp = submitFinish(reportId)
    print resp

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    logging.basicConfig(format="%(threadName)s:%(message)s")
    main(sys.argv)
    local = {}
    local.update(globals())
    local.update(locals())
    code.interact(local=local)
