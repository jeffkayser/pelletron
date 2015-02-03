#!/usr/bin/env python
# -*- coding: utf-8 -*-

import itertools
import json
import lxml.html
import os
import snowballstemmer
import sys
import unicodedata
from collections import Counter
from lxml import etree
from lxml.html.clean import Cleaner

OUTPUT_FILE = 'search.json'
SEARCH_FILETYPES = ['.html']
TAGS = ['title', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'header']
ATTRIBS = {
        'text': ['title', 'alt', 'label'],
        'url': ['href', 'src', 'cite', 'data'],
        'datetime': ['datetime'],
        }
META = ['keywords', 'description', 'author', 'creator', 'publisher']

RANKS = {
        0: TAGS,                    # Titles
        1: META,                    # Metadata
        2: ATTRIBS['text'],         # Other notable text
        3: ATTRIBS['url'],          # URLs
        4: ATTRIBS['datetime'],     # Datetimes
        }
PUNCTUATION = set(['Pc', 'Pd', 'Ps', 'Pe', 'Pi', 'Pf', 'Po'])
STOPWORDS = [
        'a', 'able', 'about', 'across', 'after', 'all', 'almost', 'also',
        'am', 'among', 'an', 'and', 'any', 'are', 'as', 'at', 'be', 'because',
        'been', 'but', 'by', 'can', 'cannot', 'could', 'dear', 'did', 'do',
        'does', 'either', 'else', 'ever', 'every', 'for', 'from', 'get', 'got',
        'had', 'has', 'have', 'he', 'her', 'hers', 'him', 'his', 'how',
        'however', 'i', 'if', 'in', 'into', 'is', 'it', 'its', 'just', 'least',
        'let', 'like', 'likely', 'may', 'me', 'might', 'most', 'must', 'my',
        'neither', 'no', 'nor', 'not', 'of', 'off', 'often', 'on', 'only',
        'or', 'other', 'our', 'own', 'rather', 'said', 'say', 'says', 'she',
        'should', 'since', 'so', 'some', 'than', 'that', 'the', 'their',
        'them', 'then', 'there', 'these', 'they', 'this', 'tis', 'to', 'too',
        'twas', 'us', 'wants', 'was', 'we', 'were', 'what', 'when', 'where',
        'which', 'while', 'who', 'whom', 'why', 'will', 'with', 'would',
        'yet', 'you', 'your',
        ]

def xpath(doc, search, ns=None):
    return doc.xpath(search)

def get_tag(doc, tag):
    return xpath(doc, '//{}'.format(tag))

def get_attrib(doc, attrib):
    return xpath(doc, '//body//*[not(self::script)][not(self::link)][@{}]'.format(attrib))

def get_meta(doc, name, attrib='content'):
    return xpath(doc, '//meta[@name="{}"][@{}]'.format(name, attrib))

def get_text(e):
    return etree.tostring(e, method='text', encoding='unicode').strip()

def get_many(doc, f, iterable):
    return list(itertools.chain.from_iterable([f(doc, item) for item in iterable]))

def get_tag_content(tag):
    return get_text(tag) if tag is not None else ''

def get_meta_content(tag):
    return tag.attrib['content'] if tag is not None and 'content' in tag.attrib else ''

def get_attrib_content(tag, attribs):
    data = []
    for attrib in attribs:
        if attrib in tag.attrib:
            data.append(tag.attrib[attrib])
    return ' '.join(data)

cleaner = Cleaner(
        scripts=True, javascript=True, comments=True, style=True,
        links=True, meta=True, page_structure=True,
        processing_instructions=True, embedded=True, frames=False,
        forms=False, annoying_tags=False, remove_tags=RANKS[0],
        kill_tags=['noscript', 'iframe'], remove_unknown_tags=False,
        safe_attrs_only=False, add_nofollow=False)

def strip_punc(text):
    return ''.join(x for x in text if unicodedata.category(x) not in PUNCTUATION)

stemmer = snowballstemmer.stemmer('english');
def get_words(text, remove_punc=True, stem=True, remove_stopwords=True):
    if remove_punc:
        text = strip_punc(text)
    words = text.split()
    if stem:
        words = Counter(stemmer.stemWords(words))
    else:
        words = Counter(text.split())
    for stopword in STOPWORDS:
        del words[stopword]
    return words

def extract_structural(doc):
    ranked = [
            get_words(u' '.join([get_tag_content(item)
                for item in get_many(doc, get_tag, RANKS[0])]).lower()),
            get_words(u' '.join([get_meta_content(item)
                for item in get_many(doc, get_meta, RANKS[1])]).lower()),
            get_words(u' '.join([get_attrib_content(item, RANKS[2])
                for item in get_many(doc, get_attrib, RANKS[2])]).lower()),
            get_words(u' '.join([get_attrib_content(item, RANKS[3])
                for item in get_many(doc, get_attrib, RANKS[3])]).lower(), remove_punc=False, stem=False),
            get_words(u' '.join([get_attrib_content(item, RANKS[4])
                for item in get_many(doc, get_attrib, RANKS[4])]).lower(), remove_punc=False, stem=False),
            ]
    return ranked

def parse_file(filename, basedir):
    print("Parsing: {}".format(filename))
    doc = lxml.html.parse(filename)
    title = get_tag_content(get_tag(doc, 'head/title')[0])
    ranked = extract_structural(doc)
    cleaner(doc)
    etree.strip_tags(doc, '*')
    text = get_text(doc.getroot()).lower()
    ranked.append(get_words(text))
    url = filename.replace(basedir, '')
    return url, title, ranked

def parse_dir(dirname):
    data = {}
    for root, dirs, files in os.walk(dirname):
        for filename in files:
            if os.path.splitext(os.path.split(filename)[-1])[-1] in SEARCH_FILETYPES:
                url, title, ranked = parse_file(os.path.join(root, filename), dirname)
                data.update({url: [title, ranked]})
    return data

def consolidate_ranks(url_ranks):
    """Consolidate search index into the following format:
        {
            "urls": ["<url-1>", ..., "<url-n>"],
            "titles": ["<title-for-url-1>", ..., "<title-for-url-n>"],
            "words": {
                "word-1": {
                    <url-index-1>: [
                        [rank-1, freq-for-rank-1]
                          :
                        [rank-n, freq-for-rank-n]
                        ],
                      :
                    <url-index-n>: [
                        [rank-1, freq-for-rank-1]
                          :
                        [rank-n, freq-for-rank-n]
                        ],
                }
                "word-n": {
                    :
                }
            }
        }
    """
    urls = url_ranks.keys()
    titles = []
    consolidated = {"urls": urls, "titles": titles, "words": {}}
    urlmap = dict(zip(list(url_ranks.keys()), range(len(url_ranks.keys()))))
    for url, (title, ranked) in url_ranks.items():
        key = urlmap[url]
        titles.append(title)
        for rank, words in enumerate(ranked):
            for word in words.keys():
                freq = words[word]
                if word not in consolidated['words']:
                    consolidated['words'][word] = {}
                if key not in consolidated['words'][word]:
                    consolidated['words'][word][key] = []
                consolidated['words'][word][key].append([rank, freq])
    return consolidated

def build_search_index(target_dir):
    consolidated = consolidate_ranks(parse_dir(target_dir))
    with open(os.path.join(target_dir, OUTPUT_FILE), 'w') as f:
        json.dump(consolidated, f)

if __name__ == '__main__':
    build_search_index(sys.argv[1])
