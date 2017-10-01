# -*- coding: UTF-8 -*-
import os
import magic
from fnmatch import fnmatch
from PyPDF2 import PdfFileReader
from searchISBN import *
import re
import argparse

#-----Argument parsing-------#
parser = argparse.ArgumentParser( description="BAO takes a directory that contains many pdf files and "
				"analyzes them, to tag the files with the correct metadata." )

parser.add_argument( 'directory', nargs = 1, type=str, help='The directory that contains the'
        ' pdf file to analyze', metavar='DIRECTORY' )

parser.add_argument( '-p', '--pattern', nargs = 1,
         dest='pattern', type=str, required=False, default=['*'], help='The pattern the file have to match to be'
         ' analyzed', metavar='PATTERN' )

parser.add_argument( '--tmp-directory', nargs = 1, dest='tmp_directory', type=str, required=False, 
                    default=['/tmp/BAO'], help='The directory where all temporary files required by the script are'
                    ' created.' , metavar='TMP_DIRECTORY' )

args = parser.parse_args()

#----------------------------#

type_stat = {}
total_files = 0.0
metadata = {}

books = []

if not os.path.exists( args.tmp_directory[0] ):
    os.makedirs( args.tmp_directory[0] )

for path, subdirs, files in os.walk(args.directory[0]):
    for name in files:
        if fnmatch(name, args.pattern[0]):
            total_files += 1 #Statistics

            try:
                ftype = magic.from_file( os.path.join(path, name), mime=True)
            except:
                f = open( os.path.join(path, name), "r")
                ftype = magic.detect_from_fobj( f ).mime_type
                f.close()

            if ftype in type_stat: #Statistics
                type_stat[ftype] += 1
            else:
                type_stat[ftype] = 1.0

            #Metadata research for PDF
            if ftype == 'application/pdf':
                print "[analyzing]\t" + os.path.join(path, name) + " ..."

                current_book = {} #A dictionary containing all the data collected for the book. __TODO__ use a fuckin' database
                current_book['path'] = os.path.join(path, name)

                f = open( os.path.join(path, name), "rb" )
                try:
                    pdf_toread = PdfFileReader( f )
                except:
                    print "[analyzing]\tPdfFileReader cannot open this file. Skipping analysis."
                    break #Pass to the next book
 
                try: #Sometimes this allow to read some PDFs
                    if pdf_toread.isEncrypted:
                        pdf_toread.decrypt('')
                except:
                    print "[decrypt]\tFailed decryption"

                try: #Extract metadata from PDF
                    pdf_info = pdf_toread.getDocumentInfo()
                except:
                    pdf_info = {}
                if type( pdf_info ) != dict:
                    pdf_info = {}

                for mdt in pdf_info.keys(): #Statistics
                    if mdt in metadata:
                        metadata[mdt] += 1
                    else:
                        metadata[mdt] = 1.0

                if '/Author' in pdf_info.keys():
                    current_book['author'] = pdf_info['/Author']
                else :
                    current_book['author'] = None
                if  '/Title' in pdf_info.keys():
                    current_book['title'] = pdf_info['/Title']
                else :
                    current_book['title'] = None

                print "[ISBNsrch]\tTrying extracting text from metadata." 
                #First strategy: try to extract the ISBN strings from the 'content' metadata
                try:
                    cnt = getTextFromMetadata( os.path.join(path, name) )
                    if len( cnt ) != 0:
                        print '[ISBNsrch]\tText layer extracted.'

                    if cnt.find('ISBN') < 0:#If there is no recurrency of 'ISBN', try to extract with slater.
                        cnt = ''
                except:
                    cnt = ''

                if len( cnt ) == 0:
                    #Second strategy: try to extract pdf layer with pdfminer/slater and then look for ISBN
                    print "[ISBNsrch]\tFailed extracting text from metadata."
                    print "[ISBNsrch]\tTrying extracting text with slate."
                    try:
                        cnt = getTextWithSlate( os.path.join(path, name), temporary_file_directory = args.tmp_directory[0] )
                        #Frequently slater returns strings with a lot of chr(12) for pdf with no text layer
                        #instead of ''.
                        if len( cnt.replace(chr(12), '' ) ) != 0: 
                            print "[ISBNsrch]\tText layer extracted."
                        else:
                            cnt = ''
                    except:
                        cnt = ''

                if len( cnt ) == 0:
                    #Last strategy: try to do an OCR on the first 10 pages of the PDF.
                    print "[ISBNsrch]\tFailed extracting text with slate."
                    print "[ISBNsrch]\tNo text layer."
                    print "[ISBNsrch]\tExecuting OCR on first and last 10 pages..."
                    try:
                        cnt = getTextWithOCR( os.path.join(path, name), temporary_file_directory = args.tmp_directory[0] )
                        if len( cnt ) != 0:
                            print "[ISBNsrch]\tText layer extracted."
                    except:
                        cnt = ''

                #Once finished, look for ISBN strings in the text
                if len( cnt ) == 0:
                    print "[ISBNsrch]\tFailed extracting text with Tesseract"
                    ISBNstrings = None
                else:
                    ISBNstrings = searchISBNstrings( cnt )

                if ISBNstrings is None:
                    print "[ISBNsrch]\t\x1b[31m No ISBN string found. \x1b[0m"
                else:
                    print "[ISBNsrch]\t\x1b[34m Found", len(ISBNstrings),"ISBN strings.\x1b[0m"
                
                #Replace with database calls
                current_book['isbn'] = ISBNstrings
                books.append(current_book)

                #Close the file
                f.close()

os.removedirs( args.tmp_directory[0] )

print "*****FILE TYPE ANALYSIS*****"
for types in type_stat.keys():
    print "* ", int( type_stat[types] ), "/", int( total_files ), "(", round(type_stat[types] / total_files * 100, 1), "%) are ", types
print
print "*****FILE METADATA ANALYSIS*****"
for mdt in metadata.keys():
    if mdt == '/Author' or mdt == '/Title':
        print "\x1b[31m",
    print "* ", int( metadata[mdt] ) , "/", int( type_stat['application/pdf'] ), "(", round(metadata[mdt]/type_stat['application/pdf'] * 100, 1), "%) are tagged with", mdt,
    print "\x1b[0m"

print "********************************"
print
