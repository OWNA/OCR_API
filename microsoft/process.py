#!/usr/bin/python

import argparse
import os
import requests
import urllib

key = os.environ["MICROSOFT_CV_TOKEN"]

params = {
    'language': 'unk',
    'detectOrientation': 'true'
}
url = 'https://westus.api.cognitive.microsoft.com/vision/v1.0/ocr?'
headers = {
    'Ocp-Apim-Subscription-Key': key,
    'Content-Type': 'application/octet-stream'
}

parser = argparse.ArgumentParser( description="Recognize a file via web service" )
parser.add_argument( 'sourceFile' )
parser.add_argument( 'targetFile' )

args = parser.parse_args()

sourceFile = args.sourceFile
targetFile = args.targetFile


if os.path.isfile(sourceFile):
    if os.path.isfile(targetFile):
        print "Target file alreadt exists, skipping"
    else:
        print "Processing %s" % sourceFile
        r = requests.post(url + urllib.urlencode(params),
                          headers=headers, data=open(sourceFile))
        f = open(targetFile, 'w')
        f.write(r.content)
        f.close()
else:
    print "No such file: %s" % sourceFile
