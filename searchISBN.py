import PyPDF2
import cStringIO
import sys, os
import re
import commands
import xmltodict as xmlparser
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

def evilMetadataFromISBN( isbn ):
    """To avoid to use the official API (it require some time for activation),
    I simply download the whole page (it's not a true research, I just suppose that
    the page exist..) and search for the bibtex entry. It is evil and stupid, use
    the API."""

    mdt = {}
    answare= commands.getoutput("curl \'http://isbnplus.com/"+isbn+"\' -s")
    pos = answare.find("author={")
    d=0
    if pos != -1:
        while answare[pos+d] != '}':
            d = d+1
    mdt['author'] = answare[pos+8:pos+d]

    pos = answare.find("title={")
    d=0
    if pos != -1:
        while answare[pos+d] != '}':
            d = d+1
    mdt['title'] = answare[pos+7:pos+d]
    return mdt

def metadataFromISBN( isbn ):
    query = 'https://api-2445581351187.apicast.io/search?q='+isbn+'&app_id='+ISBNPLUS_APP_ID+'&app_key='+ISBNPLUS_APP_KEY
    body = commands.getoutput("curl \'"+query+"\' -s")
    xmld = xmlparser.parse( body )

    mtd = {}
    mtd['author']=''
    mtd['title'] =''
    print xmld['response']['page']['total']
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

def searchISBNstrings( path, ocr_enable = True ):
    try:
        cnt = getPDFContent(path).encode("ascii", "ignore")
    except:
        print "Can't get the text from PDF."
        return None
    #print cnt
    if len( cnt ) == 0 and ocr_enable:
        print "No text layer."
        print "Executing OCR on first and last 10 pages..."
        stripFirstAndLast10Pages( path, '/tmp/stripped.pdf' )
        ocr = pypdfocr.PyPDFOCR()
        ocr.go( ['/tmp/stripped.pdf'] )
        return searchISBNstrings( '/tmp/stripped_ocr.pdf', False )
        os.remove('/tmp/stripped.pdf')
        os.remove('/tmp/stripped_ocr.pdf')

    bg = 0
    out = []
    pos = cnt.find("ISBN")
    while pos != -1 :
        #print cnt[pos:pos+23],
        strippedisbn = re.sub("\D", "", cnt[pos:pos+23])
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
        print 'Non e\' stato possibile aprire il file di input specificato, controlla l\'indirizzo e i permessi',
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
