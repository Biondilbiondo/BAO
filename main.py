# -*- coding: UTF-8 -*-
import os
import magic
from fnmatch import fnmatch
from pyPdf import PdfFileReader

root = '/home/mattia/Nextcloud/Università/Libreria/'
pattern = "*"

type_stat = {}
total_files = 0.0
metadata = {}

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
                f.close()

print "*****FILE TYPE ANALYSIS*****"
for types in type_stat.keys():
    print "* ", int( type_stat[types] ), "/", int( total_files ), "(", round(type_stat[types] / total_files * 100, 1), "%) are ", types
print
print "*****FILE METADATA ANALYSIS*****"
for mdt in metadata.keys():
    if mdt == '/Author' or mdt == '/Title':
        print "\x1b[31m",
    print "* ", int( metadata[mdt] ) , "/", int( type_stat['application/pdf'] ), "(", round(metadata[mdt]/type_stat['application/pdf'] * 100, 1), "%) are tagged with", mdt,s
    print "\x1b[0m"
