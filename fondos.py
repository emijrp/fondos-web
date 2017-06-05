#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2017 emijrp <emijrp@gmail.com>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import json
import re
import urllib.request

translations = {
    "es": {
        "Birds": "Aves", 
    }, 
}
categories = {
    "Birds": ["Featured pictures of birds"], 
}

def getAuthor(text=''):
    author = ''
    m = re.findall(r"(?im)\|\s*Author\s*=\s*(.*?)\n", text)
    if m:
        author = m[0]
    author = re.sub(r"(?im)\[\[([^\[\]\|]*?)\|([^\[\]\|]*?)\]\]", r"\2", author)
    author = re.sub(r"(?im)\[\[([^\[\]\|]*?)\]\]", r"\1", author)
    author = re.sub(r"(?im)\[([^\[\]\| ]*?)([^\[\]\|]*?)\]", r"\1", author)
    return author

def getImagesFromCategory(commonscat=''):
    images = []
    gcmcontinue = "unknown"
    while gcmcontinue:
        query = 'https://commons.wikimedia.org/w/api.php?action=query&generator=categorymembers&gcmnamespace=6&gcmtitle='
        query += 'Category:' + re.sub(' ', '%20', commonscat)
        query += '&prop=imageinfo|revisions&iiprop=url|size&rvprop=content&format=json'
        if gcmcontinue and gcmcontinue != "unknown":
            query += '&gcmcontinue=' + gcmcontinue
        raw = getURL(query)
        json1 = json.loads(raw)
        if 'query' in json1:
            if 'pages' in json1['query']:
                for page, props in json1['query']['pages'].items():
                    title = props["title"]
                    author = getAuthor(props["revisions"][0]["*"])
                    width = props["imageinfo"][0]["width"]
                    height = props["imageinfo"][0]["height"]
                    if height > width:
                        continue
                    if width < 1920:
                        continue
                    url = props["imageinfo"][0]["url"]
                    urldesc = props["imageinfo"][0]["descriptionurl"]
                    dic = {
                        "title": title, 
                        "url": url, 
                        "urldesc": urldesc, 
                        "urlthumb": re.sub(r"/commons/", r"/commons/thumb/", url) + '/200px-' + url.split('/')[-1], 
                        "urlthumb1240px": re.sub(r"/commons/", r"/commons/thumb/", url) + '/1240px-' + url.split('/')[-1], 
                        "urlthumb1440px": re.sub(r"/commons/", r"/commons/thumb/", url) + '/1440px-' + url.split('/')[-1], 
                        "urlthumb1600px": re.sub(r"/commons/", r"/commons/thumb/", url) + '/1600px-' + url.split('/')[-1], 
                        "urlthumb1920px": re.sub(r"/commons/", r"/commons/thumb/", url) + '/1920px-' + url.split('/')[-1], 
                        "author": author, 
                    }
                    images.append([title, dic])
        if 'continue' in json1:
            if 'gcmcontinue' in json1['continue']:
                gcmcontinue = json1['continue']['gcmcontinue']
                continue
        gcmcontinue = ''
    return images

def getSubcategories(commonscat=''):
    subcategories = [commonscat]
    gcmcontinue = "unknown"
    while gcmcontinue:
        query = 'https://commons.wikimedia.org/w/api.php?action=query&list=categorymembers&cmnamespace=14'
        query += '&cmtitle=Category:' + re.sub(' ', '%20', commonscat)
        query += '&format=json'
        if gcmcontinue and gcmcontinue != "unknown":
            query += '&gcmcontinue=' + gcmcontinue
        raw = getURL(query)
        json1 = json.loads(raw)
        if 'query' in json1:
            if 'categorymembers' in json1['query']:
                for cat in json1['query']['categorymembers']:
                    subcategories.append(cat["title"].split('Category:')[1])
        
        if 'continue' in json1:
            if 'gcmcontinue' in json1['continue']:
                gcmcontinue = json1['continue']['gcmcontinue']
                continue
        gcmcontinue = ''
    return subcategories

def getURL(url=''):
    f = urllib.request.urlopen(url)
    raw = f.read()
    return raw.decode("utf-8")

def main():
    lang = "es"
    #categories
    menulist = []
    for catname, commonscats in categories.items():
        print(catname)
        output = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html lang="en" dir="ltr" xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>%s - Los mejores fondos de pantalla del mundo</title>
    <meta http-equiv="content-type" content="text/html;charset=utf-8" />
    
</head>
<body>
""" % (translations[lang][catname])
        commonscats2 = commonscats
        for commonscat in commonscats2:
            commonscats = commonscats + getSubcategories(commonscat)
        commonscats = list(set(commonscats))
        commonscats.sort()
        for commonscat in commonscats:
            print(commonscat)
            images = getImagesFromCategory(commonscat)
            images.sort()
            for title, props in images:
                output += """
<div style="float: left; width: 200px;height: 300px;padding: 5px;margin: 2px;background-color: lightyellow;border: 1px solid orange;">
<a href="%s"><img src="%s" width="200px" height="150px" /></a>
<br/>
<center><a href="%s">%s</a> / Commons</center>
<br/>
<center>Tamaños:<br/><a href="%s">1240px</a> · <a href="%s">1440px</a><br/><a href="%s">1600px</a> · <a href="%s">1920px</a></center>
</div>
""" % (props["urldesc"], props["urlthumb"], props["urldesc"], props["author"], props["urlthumb1240px"], props["urlthumb1440px"], props["urlthumb1600px"], props["urlthumb1920px"])
        output += """
</body>
</html>"""
        filelabel = translations[lang][catname]
        filehtml = "%s.html" % (re.sub(' ', '-', translations[lang][catname].lower()))
        menulist.append([filelabel, filehtml])
        with open(filehtml, "w") as f:
            f.write(output)
    
    #index
    menu = ""
    for menuitem in menulist:
        menu += '<a href="%s">%s</a>' % (menuitem[1], menuitem[0])
    index = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html lang="en" dir="ltr" xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>Los mejores fondos de pantalla del mundo</title>
    <meta http-equiv="content-type" content="text/html;charset=utf-8" />
    
</head>
<body>
%s
</body>
</html>""" % (menu)
    with open("index.html", "w") as f:
        f.write(index)

if __name__ == '__main__':
    main()
