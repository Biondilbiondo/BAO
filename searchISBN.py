# -*- coding: UTF-8 -*-
import PyPDF2
import cStringIO
import sys, os
import re
import commands
import xmltodict as xmlparser
import slate
from pypdfocr import pypdfocr as pypdfocr

from time import sleep

import isbnPLUS
import OpenLibrary

def getPDFContent(path):
    content = ""
    num_pages = 10
    inpdf = PyPDF2.PdfFileReader(path)
    for i in range(0, num_pages):
        content += inpdf.getPage(i).extractText() + "\n"
    content = " ".join(content.replace(u"\xa0", " ").strip().split())
    return content

def getTextFromMetadata( path ):
    return getPDFContent(path).encode("ascii", "ignore")

def getTextWithSlate( path, temporary_file_directory = '/tmp' ):
    tmp_file_path = temporary_file_directory + '/stripped.pdf'
    stripFirstAndLast10Pages( path, tmp_file_path )
    sleep(1000)
    f = open(tmp_file_path, "r")
    texts=slate.PDF(f)
    cnt = ""
    for pg in texts:
        cnt+=pg
    f.close()
    os.remove(tmp_file_path)
    return cnt

def getTextWithOCR( path, temporary_file_directory = '/tmp' ):
    tmp_file_path = temporary_file_directory + '/stripped.pdf'
    stripFirstAndLast10Pages( path, tmp_file_path )
    ocr = pypdfocr.PyPDFOCR()
    ocr.go( [tmp_file_path] )
    os.remove(tmp_file_path)
    tmp_ocr_path = emporary_file_directory + '/stripped_ocr.pdf'
    cnt = getTextFromMetadata( tmp_ocr_path )
    os.remove( tmp_ocr_path )
    return cnt


def searchISBNstrings( cnt ):
    bg = 0
    out = []
    #Da migliorare!
    pos = cnt.find("ISBN")
    while pos != -1 :
        old_len=len(out)
        print "\x1b[33m[debug]\x1b[0m\t\tISBN string detected:\x1b[1m", cnt[pos:pos+40], "\x1b[22m"

        strippedisbn = ''
        isbnstr=cnt[pos:pos+40]
        for i in range( len(isbnstr) ):
            if isbnstr[i].isdigit() :
                strippedisbn += isbnstr[i]
            if  isbnstr[i] == 'x' or isbnstr[i] == 'X':#Se e' una X
                if len(strippedisbn) == 9 or ( len(strippedisbn) == 11 and strippedisbn[0:2] == '10' ):#e se e' nella posizione corretta per essere un carattere di controllo ISBN10
                    strippedisbn += isbnstr[i]

        #strippedisbn = re.sub("\D", "", cnt[pos:pos+40]) #Elimina i caratteri che non sono numeri
        print "\x1b[33m[debug]\x1b[0m\t\tStripped ISBN:", strippedisbn
        if len( strippedisbn ) >= 10: #Se ci sono meno di dieci numeri, boh che cazzo e'?
            if strippedisbn[0:2] == '10' and len( strippedisbn ) >= 12: #Puo' essere un ISBN10 con 10 davanti o un ISBN 10 senza il 10 davanti
                print "\x1b[33m[debug]\x1b[0m\t\tPenso sia un ISBN10."
                if checkISBN10( strippedisbn[2:12] ):
                     out.append( strippedisbn[2:12] )
                     print "\x1b[33m[debug]\x1b[0m\t\tAggiunto:\x1b[1m", out[len(out)-1], "\x1b[22m ",
                     isbnPLUS.printMetadataForISBN( out[len(out)-1] )
                     OpenLibrary.printMetadataForISBN( out[len(out)-1] )
                     print
                if checkISBN10( strippedisbn[0:10] ):
                     out.append( strippedisbn[0:10] )
                     print "\x1b[33m[debug]\x1b[0m\t\tAggiunto:\x1b[1m", out[len(out)-1], "\x1b[22m ",
                     isbnPLUS.printMetadataForISBN( out[len(out)-1] )
                     OpenLibrary.printMetadataForISBN( out[len(out)-1] )
                     print
            elif strippedisbn[0:2] == '13':#Puo' essere un ISBN10 che comincia con 13 oppure un ISBN13 con 13 davanti. Non può essere ISBN13 che inizia con 13 perché le prime 3 cifre sono sempre 978 per ISBN13
                print "\x1b[33m[debug]\x1b[0m\t\tPenso sia un ISBN13."
                if checkISBN10( strippedisbn[0:10] ):
                     out.append( strippedisbn[0:10] )
                     print "\x1b[33m[debug]\x1b[0m\t\tAggiunto:\x1b[1m", out[len(out)-1], "\x1b[22m ",
                     isbnPLUS.printMetadataForISBN( out[len(out)-1] )
                     OpenLibrary.printMetadataForISBN( out[len(out)-1] )
                     print
                if checkISBN13( strippedisbn[2:15] ):
                    out.append( strippedisbn[2:15] )
                    print "\x1b[33m[debug]\x1b[0m\t\tAggiunto:\x1b[1m", out[len(out)-1], "\x1b[22m ",
                    isbnPLUS.printMetadataForISBN( out[len(out)-1] )
                    OpenLibrary.printMetadataForISBN( out[len(out)-1] )
                    print
            else:
                print "\x1b[33m[debug]\x1b[0m\t\tNon so se sia un ISBN10 o un ISBN13."
                if checkISBN13( strippedisbn[0:13] ):
                    out.append( strippedisbn[0:13] )
                    print "\x1b[33m[debug]\x1b[0m\t\tAggiunto:\x1b[1m", out[len(out)-1], "\x1b[22m ",
                    isbnPLUS.printMetadataForISBN( out[len(out)-1] )
                    OpenLibrary.printMetadataForISBN( out[len(out)-1] )
                    print
                if checkISBN10( strippedisbn[0:10] ):
                    out.append( strippedisbn[0:10] )
                    print "\x1b[33m[debug]\x1b[0m\t\tAggiunto:\x1b[1m", out[len(out)-1], "\x1b[22m ",
                    isbnPLUS.printMetadataForISBN( out[len(out)-1] )
                    OpenLibrary.printMetadataForISBN( out[len(out)-1] )
                    print
        if len(out) == old_len:
            print "\x1b[33m[debug]\x1b[0m\t\t\x1b[1m\x1b[34mNon ho aggiunto nulla.\x1b[22m\x1b[0m "
        bg = pos
        pos = cnt.find("ISBN", bg+1 )

    if len( out ) == 0:
        return None
    else:
        return out

def checkISBN10( isbn ):
    if len( isbn ) != 10 :
        return False
    if not ( isbn[0:9].isdigit() and ( isbn[9].isdigit() or isbn[9] == 'X' or isbn[9] == 'x' ) ):
         return False

    checksum = 0
    multiplier = 10
    for char in isbn[0:9]:
        checksum += int( char ) * multiplier
        multiplier -= 1
    checksum = ( 11 - ( checksum % 11 ) ) % 11
    if ( isbn[9] == 'x' or isbn[9] == 'X' ):
        if checksum == 10:
            return True
        else:
            return False
    if checksum == int( isbn[9] ):
        return True
    return False

def checkISBN13( isbn ):
    if len( isbn ) != 13 :
        return False
    if not isbn[0:13].isdigit() :
         return False

    checksum = 0
    multiplier = 1
    for char in isbn[0:12]:
        checksum += int( char ) * multiplier
        if multiplier == 1:
            multiplier = 3
        else:
            multiplier = 1

    checksum = 10 - ( checksum % 10 )
    if checksum == 10 and int( isbn[12] ) == 0:
        return True
    if checksum == int( isbn[12] ):
        return True
    if checkISBN10(isbn[3:]): #Spesso trovo ISBN13 con la cifra di controllo non ricalcolata, ovvero la giustapposizione delle tre cifre 978 e dell'ISBN10, cosi' passano come buoni
        return True
    return False

def stripFirstAndLast10Pages( infile, outfile ):
    #Prova ad aprire il file di input
    try:
        book = PyPDF2.PdfFileReader( infile )
    except:
        print '[Tesseract]\tNon e\' stato possibile aprire il file di input specificato, controlla l\'indirizzo e i permessi',
        print 'di accesso al file.'
        exit()
        #Prova ad aprire il file di output
    #Prova ad aprire il file di output
    try:
        outf = open( outfile, "wb+" )
    except:
        print 'Non e\' stato possibile creare il file di output specificato, controlla i permessi',
        print 'di scrittura nella cartella specificata.'
        exit()

    stripped_book = PyPDF2.PdfFileWriter()
    for i in range( 10 ):
        stripped_book.addPage( book.getPage( i ) )
    num_pg = book.getNumPages()
    for i in range( 10 ):
        stripped_book.addPage( book.getPage( num_pg - i - 1 ) )
    stripped_book.write(outf)
    outf.close()
