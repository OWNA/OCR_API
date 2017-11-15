import os
import sys
import time
import urllib2

from AbbyyOnlineSdk import *


processor = AbbyyOnlineSdk()

if "ABBYY_APPID" in os.environ:
	processor.ApplicationId = os.environ["ABBYY_APPID"]

if "ABBYY_PWD" in os.environ:
	processor.Password = os.environ["ABBYY_PWD"]

print 'ApplicationId:"{0}", Password:"{1}"'.format(processor.ApplicationId, processor.Password)
# Proxy settings
if "http_proxy" in os.environ:
	proxyString = os.environ["http_proxy"]
	print "Using proxy at %s" % proxyString
	processor.Proxy = urllib2.ProxyHandler( { "http" : proxyString })


# Recognize a file at filePath and save result to resultFilePath
def recognizeFile(filePath,
                  resultFilePath,
                  settings,
                  processReceipt=False,
                  processFields=False,
                  fieldSettings=None):
	print "Uploading.."
        if processFields:
                task = processor.SubmitImage( filePath )
                task = processor.ProcessFields( task.Id, fieldSettings )
        elif processReceipt:
	        task = processor.ProcessReceipt( filePath, settings )
        else:
	        task = processor.ProcessImage( filePath, settings )
	if task == None:
		print "Error"
		return
	print "Id = %s" % task.Id
	print "Status = %s" % task.Status

	# Wait for the task to be completed
	sys.stdout.write( "Waiting.." )
	# Note: it's recommended that your application waits at least 2 seconds
	# before making the first getTaskStatus request and also between such requests
	# for the same task. Making requests more often will not improve your
	# application performance.
	# Note: if your application queues several files and waits for them
	# it's recommended that you use listFinishedTasks instead (which is described
	# at http://ocrsdk.com/documentation/apireference/listFinishedTasks/).

	while task.IsActive() == True :
		time.sleep( 5 )
		sys.stdout.write( "." )
		task = processor.GetTaskStatus( task )

	print "Status = %s" % task.Status
	if task.Status == "Completed":
		if task.DownloadUrl != None:
			processor.DownloadResult(task.DownloadUrl, resultFilePath)
			print "Result was written to %s" % resultFilePath
		if task.DownloadUrl2 != None:
                        resultFilePath2 = resultFilePath + '2'
			processor.DownloadResult(task.DownloadUrl2, resultFilePath2)
			print "Result2 was written to %s" % resultFilePath2
	else:
		print "Error processing task %s" % task.Error

