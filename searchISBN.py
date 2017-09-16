import PyPDF2
import cStringIO
import sys, os
import re
import commands
import xmltodict as xmlparser
import slate
from pypdfocr import pypdfocr as pypdfocr

ISBNPLUS_APP_ID = 'd6303441'
ISBNPLUS_APP_KEY = '07b60ccae2f7f2bb0e8acbc1dbbeb540'


def getPDFContent(path):
    content = ""
    num_pages = 10
    inpdf = PyPDF2.PdfFileReader(path)
    for i in range(0, num_pages):
        content += inpdf.getPage(i).extractText() + "\n"
    content = " ".join(content.replace(u"\xa0", " ").strip().split())
    return content

def isValidISBNAnsware( metadata ):
    try:
        metadata = json.loads( answare )
    except:
        return False
    return True

def metadataFromISBN( isbn ):
    query = 'https://api-2445581351187.apicast.io/search?q='+isbn+'&app_id='+ISBNPLUS_APP_ID+'&app_key='+ISBNPLUS_APP_KEY
    body = commands.getoutput("curl \'"+query+"\' -s")
    xmld = xmlparser.parse( body )

    mtd = {}
    mtd['author']=''
    mtd['title'] =''
    if int(xmld['response']['page']['total']) > 0:
        if  type( xmld['response']['page']['results']['book'] ) == list :
            mtd['title'] = xmld['response']['page']['results']['book'][0]['title']
            mtd['author'] = xmld['response']['page']['results']['book'][0]['author']
        else:
            mtd['title'] = xmld['response']['page']['results']['book']['title']
            mtd['author'] = xmld['response']['page']['results']['book']['author']
    return mtd


def metadataISBNGetAuthor( mdt ):
    if 'author' in mdt['list'][0]:
        return mdt['list'][0]['author']
    else:
        return None

def metadataISBNGetTitle( mdt ):
    if 'title' in mdt['list'][0]:
        return mdt['list'][0]['title']
    else:
        return None

def pdf_to_text(_pdf_file_path):
    pdf_content = PyPDF2.PdfFileReader(file(_pdf_file_path, "rb"))
    text_extracted = ""
    for x in range(0, 20):
        pdf_text = ""  # A variable to store text extracted from a page
        pdf_text = pdf_text + pdf_content.getPage(x).extractText()
        text_extracted = text_extracted + "\n\n\n"
    num_pg = book.getNumPages()
    for x in range(num_pg-21, num_pg-1):
        pdf_text = ""  # A variable to store text extracted from a page
        pdf_text = pdf_text + pdf_content.getPage(x).extractText()
        text_extracted = text_extracted + "\n\n\n"
    return text_extracted

def getTextFromMetadata( path ):
    return getPDFContent(path).encode("ascii", "ignore")

def getTextWithSlate( path ):
    stripFirstAndLast10Pages( path, '/tmp/stripped.pdf' )
    f = open('/tmp/stripped.pdf', "r")
    texts=slate.PDF(f)
    cnt = ""
    for pg in texts:
        cnt+=pg
    f.close()
    os.remove('/tmp/stripped.pdf')
    return cnt

def getTextWithOCR( path ):
    stripFirstAndLast10Pages( path, '/tmp/stripped.pdf' )
    ocr = pypdfocr.PyPDFOCR()
    ocr.go( ['/tmp/stripped.pdf'] )
    os.remove('/tmp/stripped.pdf')
    cnt = getTextFromMetadata( '/tmp/stripped_ocr.pdf' )
    os.remove('/tmp/stripped_ocr.pdf')
    return cnt


def searchISBNstrings( cnt):
    bg = 0
    out = []
    #Da migliorare!
    pos = cnt.find("ISBN")
    while pos != -1 :
        print "\x1b[33m[debug]\x1b[0m\t\tISBN string detected:", cnt[pos:pos+28]
        strippedisbn = re.sub("\D", "", cnt[pos:pos+28])
        if not any( strippedisbn in s for s in out ):
            if len ( strippedisbn ) == 10 or len( strippedisbn ) == 13:
                out.append(strippedisbn)
            elif len( strippedisbn ) == 12 and strippedisbn[0:2] == '10':
                out.append(strippedisbn[2:12])
            elif len( strippedisbn ) == 15 and strippedisbn[0:2] == '13':
                out.append(strippedisbn[2:15])
        bg = pos
        pos = cnt.find("ISBN", bg+1 )
    if len( out ) == 0:
        return None
    else:
        return out


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
