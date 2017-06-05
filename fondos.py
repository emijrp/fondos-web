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
import random
import re
import unicodedata
import urllib.request

translations = {
    "es": {
        "Amphibians": "Anfibios", 
        "Architecture": "Arquitectura", 
        "Astronomy": "Astronomía", 
        "Birds": "Aves", 
        "Fish": "Peces", 
        "Insects": "Insectos", 
        "Mammals": "Mamíferos", 
        "Molluscs": "Moluscos", 
        "Objects": "Objetos", 
        "Oceans": "Océanos", 
        "Landscapes": "Paisajes", 
        "Plants": "Plantas", 
        "Reptiles": "Reptiles", 
        "Spiders": "Arañas", 
        "Transport": "Transporte", 
        "See info": "Ver info", 
    }, 
}
categories = {
    "Amphibians": ["Featured pictures of amphibians"], 
    "Architecture": ["Featured pictures of architecture"], 
    "Astronomy": ["Featured pictures of astronomy"], 
    "Birds": ["Featured pictures of birds"], 
    "Fish": ["Featured pictures of fish"], 
    "Insects": ["Featured pictures of insects"], 
    "Landscapes": ["Featured pictures of landscapes"], 
    "Mammals": ["Featured pictures of mammals"], 
    "Molluscs": ["Featured pictures of molluscs"], 
    "Objects": ["Featured pictures of objects"], 
    "Oceans": ["Featured pictures of oceans"], 
    "Plants": ["Featured pictures of plants"], 
    "Reptiles": ["Featured pictures of reptiles"], 
    "Spiders": ["Featured pictures of spiders"], 
    "Transport": ["Featured pictures of transport"], 
}

def removeaccents(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn')
                  
def getAuthor(text=''):
    author = ''
    m = re.findall(r"(?im)\|\s*Author\s*=\s*(.*?)\n", text)
    if m:
        author = m[0].strip()
    author = re.sub(r"(?im)\[\[([^\[\]\|]*?)\|([^\[\]\|]*?)\]\]", r"\2", author)
    author = re.sub(r"(?im)\[\[([^\[\]\|]*?)\]\]", r"\1", author)
    author = re.sub(r"(?im)\[([^\[\]\| ]*?)([^\[\]\|]*?)\]", r"\1", author)
    author = re.sub(r"(?im)\{\{\s*User\s*:([^/\{\}]+?)/[^\{\}]*?\}\}", r"\1", author)
    author = re.sub(r"(?im)\{\{\s*Creator\s*:([^/\{\}]+?)\}\}", r"\1", author)
    author = re.sub(r"(?im)\{\{\s*user at project\s*\|([^|]*?)\|[^\{\}]*?\}\}", r"\1", author)
    author = re.sub(r"(?im)\[\[(Image|File):[^\[\]]*?\]\]", r"", author)
    return author.strip()

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
                    if height > width or \
                        width < 1920 or \
                        (width > height*2.5 or width < height*1.5):
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
    menulist = []
    ctotal = 0
    maingallery = []
    gallerylimit = 25
    for catname, commonscats in categories.items():
        print(catname)
        filelabel = translations[lang][catname]
        filehtmlprefix = "%s" % (re.sub(' ', '-', translations[lang][catname].lower()))
        filehtmlprefix = removeaccents(filehtmlprefix)
        filehtml = "%s.html" % (filehtmlprefix)
        commonscats2 = commonscats
        for commonscat in commonscats2:
            commonscats = commonscats + getSubcategories(commonscat)
        commonscats = list(set(commonscats))
        commonscats.sort()
        c = 0
        gallery = []
        for commonscat in commonscats:
            print(commonscat)
            images = getImagesFromCategory(commonscat)
            images.sort()
            for title, props in images:
                galleryitem = """
<div style="float: left; width: 210px;height: 300px;padding: 2px;margin: 2px;background-color: lightyellow;border: 1px solid orange;">
<a href="%s"><img src="%s" width="200px" height="140px" /></a>
<center><a href="%s">1240px</a> · <a href="%s">1440px</a><br/><a href="%s">1600px</a> · <a href="%s">1920px</a></center>
<center><br/><a href="%s">%s</a> / Commons</center>
<br/>
</div>
""" % (props["urldesc"], props["urlthumb"], props["urlthumb1240px"], props["urlthumb1440px"], props["urlthumb1600px"], props["urlthumb1920px"], props["urldesc"], props["author"] and props["author"] or translations[lang]["See info"])
                gallery.append(galleryitem)
                if random.randint(0, 9) == 0:
                    maingallery.append(galleryitem)
                c += 1
                ctotal += 1
        #random.shuffle(gallery)
        cpage = 1
        while (cpage-1) * gallerylimit <= len(gallery):
            galleryplain = ''.join(gallery[(cpage-1) * gallerylimit:cpage * gallerylimit])
            menupages = " ".join(['<a class="mw-ui-button mw-ui-blue" href="%s%s.html">%s</a>' % (filehtmlprefix, i != 1 and i or '', i) for i in range(1, int(round(len(gallery)/gallerylimit)))])
            output = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html lang="en" dir="ltr" xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>%s - Los mejores fondos de pantalla</title>
    <meta http-equiv="content-type" content="text/html;charset=utf-8" />
    
    <link rel="stylesheet" href="style.css" />
</head>
<body>
<h2><a href="%s">Fondos de pantalla de %s</a></h2>

<p>Una selección de las mejores <b>imágenes de %s</b> extraídas de <a href="https://commons.wikimedia.org">Wikimedia Commons</a> para usarlas como fondos de escritorio. Un total de %s <b>fondos de pantalla</b> con licencias libres. Haz click en las imágenes para consultar la información de autoría, licencia y otras cosas.</p>

<p><a href="index.html">&lt;&lt; Volver a la portada</a></p>

<center>
%s
</center>

<div style="margin-top: 5px;">
%s
</div>


</body>
</html>""" % (translations[lang][catname], filehtml, translations[lang][catname], translations[lang][catname], c, menupages, galleryplain)
            if cpage == 1:
                menulist.append([filelabel, filehtml])
            filehtmlpage = filehtml
            if cpage > 1:
                filehtmlpage = filehtml.split('.html')[0] + str(cpage) + '.html'
            with open(filehtmlpage, "w") as f:
                f.write(output)
            cpage += 1
    
    #index
    menulist.sort()
    menu = ""
    for menuitem in menulist:
        menu += '<a class="mw-ui-button mw-ui-blue" href="%s">%s</a> ' % (menuitem[1], menuitem[0])
    
    random.shuffle(maingallery)
    maingallery = ''.join(maingallery[:gallerylimit])
    index = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html lang="en" dir="ltr" xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>Los mejores fondos de pantalla</title>
    <meta http-equiv="content-type" content="text/html;charset=utf-8" />
    
    <link rel="stylesheet" href="style.css" />
</head>
<body>
<h2><a href="index.html">Fondos de pantalla</a></h2>

<p>Una selección de las <b>mejores imágenes</b> extraídas de <a href="https://commons.wikimedia.org">Wikimedia Commons</a> para usarlas como fondos de escritorio. Un total de <b>%s fondos</b> de pantalla con licencias libres. Haz click en las imágenes para consultar la información de autoría, licencia y descripciones.</p>

<center>%s</center>

<div style="margin-top: 5px;">
%s
</div>

<br/><br/>

</body>
</html>""" % (ctotal, menu, ''.join(maingallery))
    with open("index.html", "w") as f:
        f.write(index)

if __name__ == '__main__':
    main()
