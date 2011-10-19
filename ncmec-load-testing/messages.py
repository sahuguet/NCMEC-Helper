import libxml2
import sys

def __createReport(incident_type, url, reporting_person):
    return """<?xml version="1.0" encoding="UTF-8"?>
<report xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="espsubmittal.xsd">
  <incidentSummary>
    <incidentType>%(incident_type)s</incidentType>
  </incidentSummary>
  <internetDetails>
    <webPageIncident>
      <url>%(url)s</url>
    </webPageIncident>
  </internetDetails>
  <reporter>
    <reportingPerson>
      <firstName>%(first_name)s</firstName>
      <lastName>%(last_name)s</lastName>
      <email>%(email)s</email>
    </reportingPerson>
  </reporter>
</report>""" % { 'incident_type': incident_type,
                 'url': url,
                 'email': reporting_person['email'],
                 'first_name': reporting_person['first_name'],
                 'last_name': reporting_person['last_name'] }


def __createFileDetails(report_id, file_id, filename, details):
    return """<?xml version="1.0" encoding="UTF-8"?>
<fileDetails xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="espsubmittal.xsd">
  <reportId>%(report_id)s</reportId>
  <fileId>%(file_id)s</fileId>
  <fileName>%(filename)s</fileName>
%(details)s
</fileDetails>""" % { 'report_id': report_id,
                      'file_id': file_id,
                      'filename': filename,
                      'details': __createDetails(details) }

def __createDetails(details):
    xml = []
    for detail in details:
        xml.append('<details type="%s">' % detail['type'])
        for pair in detail['data']:
            xml.append('<nameValuePair>')
            xml.append('<name>%s</name>' % pair['name'])
            xml.append('<value>%s</value>' % pair['name'])
            xml.append('</nameValuePair>')
        xml.append('</details>')
    return ''.join(xml)


def main(argv):
    print libxml2.parseDoc(__createFileDetails('123',
                                            'aef123456',
                                            'kids.png',
                                            [ { 'type': 'EXIF',
                                                'data': [ { 'name': 'lat', 'value': '123.45' },
                                                          { 'name': 'lng', 'value': '-123.45' }] } ])
                        )

    
if __name__ == '__main__':
    main(sys.argv)
