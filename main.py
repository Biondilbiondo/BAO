# -*- coding: UTF-8 -*-
import os
import magic
from fnmatch import fnmatch
from pyPdf import PdfFileReader
from searchISBN import *
import re

root = '/home/mattia/Nextcloud/Università/Libreria'
pattern = "*"

type_stat = {}
total_files = 0.0
metadata = {}

books = []

for path, subdirs, files in os.walk(root):
    for name in files:
        if fnmatch(name, pattern):
            #print os.path.join(path, name)
            total_files += 1
            #file type analysis, the try / except is to manage different version
            #of the magic library. Should be implemented in a safer way.
            try:
                ftype = magic.from_file( os.path.join(path, name), mime=True)
            except:
                f = open( os.path.join(path, name), "r")
                ftype = magic.detect_from_fobj( f ).mime_type
                f.close()

            #print "File type: ", ftype
            if ftype in type_stat:
                type_stat[ftype] += 1
            else:
                type_stat[ftype] = 1.0

            #file metadata analysis
            if ftype == 'application/pdf':
                print "[analyzing]\t" + os.path.join(path, name) + " ..."
                current_book = {}
                current_book['path'] = os.path.join(path, name)
                f = open( os.path.join(path, name), "rb" )
                pdf_toread = PdfFileReader( f )
                if pdf_toread.isEncrypted:
                    pdf_toread.decrypt('')
                pdf_info = pdf_toread.getDocumentInfo()
                for mdt in pdf_info.keys():
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
                try:
                    cnt = getTextFromMetadata( os.path.join(path, name) )
                    if len( cnt ) != 0:
                        print "[ISBNsrch]\tText layer extracted."
                    if cnt.find('ISBN') < 0:#Se non c'è nemmeno una ricorrenza di ISBN, provo a estrarre con slater.
                        cnt = ''
                except:
                    cnt = ""

                if len( cnt ) == 0:
                    print "[ISBNsrch]\tFailed extracting text from metadata."
                    print "[ISBNsrch]\tTrying extracting text with slate."
                    try:
                        cnt = getTextWithSlate( os.path.join(path, name) )
                        if len( cnt.replace(chr(12), '' ) ) != 0:
                            print "[ISBNsrch]\tText layer extracted."
                        else:
                            cnt = ''
                    except:
                        cnt = ""

                if len( cnt ) == 0:
                    print "[ISBNsrch]\tFailed extracting text with slate."
                    print "[ISBNsrch]\tNo text layer."
                    print "[ISBNsrch]\tExecuting OCR on first and last 10 pages..."
                    try:
                        cnt = getTextWithOCR( os.path.join(path, name) )
                        if len( cnt ) != 0:
                            print "[ISBNsrch]\tText layer extracted."
                    except:
                        cnt = ""

                if len( cnt ) == 0:
                    print "[ISBNsrch]\tFailed extracting text with Tesseract"
                    ISBNstrings = None
                else:
                    ISBNstrings = searchISBNstrings( cnt )

                if ISBNstrings is None:
                    print "[ISBNsrch]\t\x1b[31m No ISBN string found. \x1b[0m"
                else:
                    print "[ISBNsrch]\t\x1b[34m Found", len(ISBNstrings),"ISBN strings.\x1b[0m"
                current_book['isbn'] = ISBNstrings

                books.append(current_book)

                f.close()

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

'''for book in books:
    print book['path']
    print "\tAuthor:", book['author']
    print "\tTitle:", book['title']
    print "\tFound ISBN: "
    if book['isbn'] is not None:
        for isbn in book['isbn']:
            mdt = metadataFromISBN( isbn )
            if mdt['author'] is not '' and mdt['title'] is not '':
                print "\x1b[34m",
            else:
                print "\x1b[31m",
            print "\t\t\t",isbn,
            print "\x1b[0m",

            if mdt['author'] is not '' and mdt['title'] is not '':
                print "( A:\x1b[33m", mdt['author'], "\x1b[0mT:\x1b[32m", mdt['title'], "\x1b[0m)",
            #Idee per il consistecy check del libro :
            #   verifica che il numero di pagine corrisponda ( +- 5% )
            #   cerca il titolo del libro nel libro stesso e guarda quante ricorrenze ci sono
            #   cerca il nome dell'autore nel libro e guarda quante ricorrenze ci sono
            #   se ci sono più ISBN verifica che non siano le versioni 10 e 13 dello stesso libro.

            print'''
