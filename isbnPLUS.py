import cStringIO
import sys, os
import re
import commands
import xmltodict as xmlparser

ISBNPLUS_APP_ID = 'd6303441'
ISBNPLUS_APP_KEY = '07b60ccae2f7f2bb0e8acbc1dbbeb540'

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

def printMetadataForISBN( isbn ):
    mdt = metadataFromISBN( isbn )
    if mdt['author'] is not '' and mdt['title'] is not '':
        print "( A:\x1b[33m", mdt['author'], "\x1b[0mT:\x1b[32m", mdt['title'], "\x1b[0m)"
    else:
        print "\x1b[31mNo metadata found.\x1b[0m"
