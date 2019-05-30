#encoding: utf8
'''
Created on 2018/06/28

@author: HOLLY
'''

import logging, argparse, sys

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)
_basic_handler = logging.StreamHandler()
_basic_handler.setLevel(logging.DEBUG)
_formatter = logging.Formatter('%(asctime)s: %(name)s: '\
                               '%(levelname)s: %(message)s')
_basic_handler.setFormatter(_formatter)
_logger.addHandler(_basic_handler)

from whoosh import index as windex
import os
from whoosh import fields as wfields
from whoosh.qparser import QueryParser
import shutil
from janome.tokenizer import Tokenizer
t = Tokenizer()

_g_flg_debug = False
DEF_index_dir = 'indexdir'
DEF_top_n = 3

def reset_index_dir(index_dir=DEF_index_dir):
    shutil.rmtree(index_dir)

def get_schema():
    schema = wfields.Schema(id=wfields.ID(stored=True, unique=True),
                            title=wfields.TEXT(stored=True),
                            title_row=wfields.STORED(),
                            content=wfields.TEXT(stored=True),
                            content_row=wfields.STORED())
    return schema

def get_whoosh_index(index_dir=DEF_index_dir):
    if not os.path.isdir(index_dir):
        schema = get_schema()
        os.makedirs(index_dir)
        ix = windex.create_in(index_dir, schema)
    else:
        ix = windex.open_dir(index_dir)
    return ix

def search_index_by_query_list(query_list, top_n=DEF_top_n, index_dir=DEF_index_dir):
    ix = get_whoosh_index(index_dir)
    search_query = ' OR '.join(query_list)
    results = search_index(ix, search_query)
    
    if len(results) > top_n:
        results = results[:top_n]
    else:
        _logger.warning('{} results have requested, but only {} results ware'
                        ' found'.format(top_n, len(results)))
    
    return results

def search_index(whoosh_index, query_text, earch_target='content'):
    ret_list = []
    with whoosh_index.searcher() as searcher:
        query = QueryParser(earch_target, whoosh_index.schema).parse(query_text)
        results = searcher.search(query)
        for result in results:
            ret_list.append({'title':result['title_row'],
                             'content':result['content_row']})
    return ret_list

content_pos = ['名詞', '動詞', '形容詞', '副詞']

def extract_contents_words(sentence):
    content_word_list = []
    for token in t.tokenize(sentence):
        _logger.debug(token)
        if token.part_of_speech.split(',')[0] in content_pos:
            content_word_list.append(token.surface)
    return content_word_list

def search_index_by_sentence(sentence, 
                             top_n=DEF_top_n, 
                             index_dir=DEF_index_dir, 
                             query_function=extract_contents_words):
    query = query_function(sentence)
    results = search_index_by_query_list(query, top_n, index_dir)
    
    return results

def main(args):
    if args.debug:
        enable_debug_mode()
    
    results = search_index_by_query_list(args.query, args.top, args.index_dir)
    
    for i, result in enumerate(results):
        if i >= args.top:
            break
        print('title: {}'.format(result['title']))
        print('content: \n{}'.format(result['content']))
        print('\n----------------------------------\n')

def set_parser():
    parser = argparse.ArgumentParser(description='')
    parser.set_defaults(func=main)
    parser.add_argument('-d', '--debug',
                        action='store_true',
                        default=False,
                        help='set debug mode (default:False)')
    
    parser.add_argument('-i', '--index-dir',
                        dest='index_dir',
                        action='store',
                        type=str,
                        default=DEF_index_dir,
                        metavar='DIRPATH',
                        help='set index directory path (default: {})'\
                             ''.format(DEF_index_dir))
    parser.add_argument('-t', '--top',
                        action='store',
                        type=int,
                        default=DEF_top_n,
                        metavar='TOP_N',
                        help='show TOP_N results (default: {})'.format(
                            DEF_top_n))
    
    parser.add_argument('query',
                        action='store',
                        type=str,
                        nargs='+',
                        metavar='QUERY',
                        help='set query to search')
    
    return parser

def enable_debug_mode():
    _g_flg_debug = True
    _logger.setLevel(logging.DEBUG)


if __name__ == '__main__':
    if '--test-mode' in sys.argv:
        import ignored_codes
        ignored_codes.search_archives()
        sys.exit()
    parser = set_parser()
    args = parser.parse_args()
    args.func(args)
