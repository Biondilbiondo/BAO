# -*- coding: UTF-8 -*-
import os
import magic
from fnmatch import fnmatch
from pyPdf import PdfFileReader
from searchISBN import *

root = '/home/mattia/Nextcloud/Università/Libreria/'
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
            #file type analysis
            ftype = magic.from_file( os.path.join(path, name), mime=True)
            #print "File type: ", ftype
            if ftype in type_stat:
                type_stat[ftype] += 1
            else:
                type_stat[ftype] = 1.0

            #file metadata analysis
            if ftype == 'application/pdf':
                print "Analyzing " + os.path.join(path, name) + " ..."
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

                ISBNstrings = searchISBNstrings(os.path.join(path, name) )
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

for book in books:
    print book['path']
    print "\tAuthor:", book['author']
    print "\tTitle:", book['title']
    print "\tFound ISBN: "
    if book['isbn'] is not None:
        for isbn in book['isbn']:
            #This function is evil. It shouldn't be used.
            mdt = evilMetadataFromISBN( isbn )
            if mdt['author'] is not '' and mdt['title'] is not '':
                print "\x1b[34m",
            else:
                print "\x1b[31m",
            print "\t\t",isbn,
            print "\x1b[0m",

            if mdt['author'] is not '' and mdt['title'] is not '':
                print "( A:\x1b[33m", mdt['author'], "\x1b[0mT:\x1b[32m", mdt['title'], "\x1b[0m)",
            #Idee per il consistecy check del libro :
            #   verifica che il numero di pagine corrisponda ( +- 5% )
            #   cerca il titolo del libro nel libro stesso e guarda quante ricorrenze ci sono
            #   cerca il nome dell'autore nel libro e guarda quante ricorrenze ci sono
            #   se ci sono più ISBN verifica che non siano le versioni 10 e 13 dello stesso libro.

            print