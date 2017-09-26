import cStringIO
import sys, os
import re
import commands
import json
import xmltodict as xmlparser

def isValidOpenLibraryAnsware( metadata ):
    try:
        metadata = json.loads( metadata )
        if metadata['status'] == 'ok' :
            return True
        else:
            return False
    except:
        return False


def metadataFromISBN( isbn ):
    mtd = {}
    mtd['author']=''
    mtd['title'] =''

    if len( isbn ) == 10:
        query = 'http://openlibrary.org/query.json?type=/type/edition&isbn_10='+isbn+"&works="
    elif len( isbn ) == 13:
        query = 'http://openlibrary.org/query.json?type=/type/edition&isbn_13='+isbn+"&works="
    else:
        return mtd
    #print "query:", query

    body = commands.getoutput("curl \'"+query+"\' -s")
    #print "result:", body
    json_query = json.loads( body )
    if len( json_query ) == 0:
        return mtd

    object_id = json_query[0]['key'].strip('\/books\/')

    query = 'http://openlibrary.org/api/get?key=/b/'+object_id+'&prettyprint;=true'
    body = commands.getoutput("curl \'"+query+"\' -s")
    #print body
    metadata = json.loads( body)
    #print metadata
    if isValidOpenLibraryAnsware( body ):
        metadata = json.loads( body )
        if metadata['result'].has_key('title'):
            mtd['title'] = metadata['result']['title']

        if metadata['result'].has_key('authors') and type(metadata['result']['authors']) == list :
            for author in metadata['result']['authors']:
                query = 'http://openlibrary.org/api/get?key=/a/'+author['key'].strip('/authors/')+'&prettyprint;=true'
                body = commands.getoutput("curl \'"+query+"\' -s")
                if isValidOpenLibraryAnsware(body):
                    auth = json.loads(body)['result']['name']
                mtd['author']+=auth+", "
        if len( mtd['author'] ) > 0:
            mtd['author']=mtd['author'][0:len(mtd['author'])-2]
    return mtd
'''
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
'''
def printMetadataForISBN( isbn ):
    mdt = metadataFromISBN( isbn )
    if mdt['author'] is not '' and mdt['title'] is not '':
        print "( S:OpenLibrary A:\x1b[33m", mdt['author'], "\x1b[0mT:\x1b[32m", mdt['title'], "\x1b[0m)",
    else:
        print "\x1b[31m( S:OpenLibrary No metadata found.)\x1b[0m",
