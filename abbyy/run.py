#!/usr/bin/python

# Usage: process.py <input file> <output file> [-language <Language>] [-pdf|-txt|-rtf|-docx|-xml|-xmlForCorrectedImage]

import argparse
import os

from process import recognizeFile
from AbbyyOnlineSdk import ProcessingSettings

parser = argparse.ArgumentParser( description="Recognize a file via web service" )
parser.add_argument( 'sourceFile' )
parser.add_argument( 'targetFile' )

parser.add_argument( '-l', '--language', default='English', help='Recognition language (default: %(default))' )
parser.add_argument( '-p', '--profile', default='documentConversion', help='Recognition profile (default: %(default))' )
parser.add_argument( '-fs', '--fieldSettings' , help='XML field settings')
group = parser.add_mutually_exclusive_group()
group.add_argument( '-txt', action='store_const', const='txt', dest='format', default='txt' )
group.add_argument( '-pdf', action='store_const', const='pdfSearchable', dest='format' )
group.add_argument( '-rtf', action='store_const', const='rtf', dest='format' )
group.add_argument( '-docx', action='store_const', const='docx', dest='format' )
group.add_argument( '-xml', action='store_const', const='xml', dest='format' )
group.add_argument( '-xmlForCorrectedImage', action='store_const', const='xmlForCorrectedImage', dest='format' )
parser.add_argument( '-var', default=True, action='store_const', const=True, dest='withVariants' )
parser.add_argument( '-receipt', default=False, action='store_const', const=True, dest='processReceipt' )
parser.add_argument( '-fields', default=False, action='store_const', const=True, dest='processFields' )

args = parser.parse_args()

sourceFile = args.sourceFile
targetFile = args.targetFile
language = args.language
outputFormat = args.format
withVariants = args.withVariants
if outputFormat != 'xml' and outputFormat != 'xmlForCorrectedImage':
        withVariants = False
processReceipt = args.processReceipt
processFields = args.processFields
profile = args.profile
fieldSettings = args.fieldSettings

if os.path.isfile(sourceFile):
        if os.path.isfile(targetFile):
                print "Target file alreadt exists, skipping"
        else:
                settings = ProcessingSettings()
                settings.Language = language
                settings.OutputFormat = outputFormat
                settings.withVariants = withVariants
                settings.Profile = profile
                print settings
                recognizeFile(sourceFile,
                              targetFile,
                              settings,
                              processReceipt=processReceipt,
                              processFields=processFields,
                              fieldSettings=fieldSettings)

else:
        print "No such file: %s" % sourceFile
