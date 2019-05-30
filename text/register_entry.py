#encoding: utf8
'''
Created on 2018/07/16

@author: HOLLY
'''

import logging, argparse, sys

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)
_basic_handler = logging.StreamHandler()
_basic_handler.setLevel(logging.INFO)
_formatter = logging.Formatter('%(asctime)s: %(name)s: '\
                               '%(levelname)s: %(message)s')
_basic_handler.setFormatter(_formatter)
_logger.addHandler(_basic_handler)

import json
import tools
import search_archives
import re

doc_pat = re.compile(r'\<DOC\>.*?\</DOC\>', re.RegexFlag.DOTALL)
headline_pat = re.compile(r'\<HEADLINE\>(.*?)\</HEADLINE\>', re.RegexFlag.DOTALL)
maintext_pat = re.compile(r'\<TEXT\>(.*?)\</TEXT\>', re.RegexFlag.DOTALL)

_g_flg_debug = False

K_id = 'id'
K_title = 'title'
K_title_row = 'title_row'
K_content = 'content'
K_content_row = 'content_row'

from janome.tokenizer import Tokenizer

t = Tokenizer()

DEF_log_filename = 'register_entry.log'

def set_file_logger(filename=DEF_log_filename):
    _file_handler = logging.FileHandler(filename=filename)
    _file_handler.setLevel(logging.DEBUG)
    _file_handler.setFormatter(_formatter)
    _logger.addHandler(_file_handler)
    _logger.debug('start file logging to {}'.format(filename))


def register_data(data_dict_list, whoosh_index):
    writer = whoosh_index.writer()
    for data in data_dict_list:
        try:
            writer.add_document(id=data[K_id],
                                title=data[K_title],
                                title_row=data[K_title_row],
                                content=data[K_content],
                                content_row=data[K_content_row])
        except:
            _logger.error('cannot register data: {}'.format(data[K_id]))
    writer.commit()
    return whoosh_index

def parse_blog_data(json_filename, encoding='utf8'):
    ret_list = []
    with open(json_filename, 'r', encoding=encoding) as infile:
        datas = json.load(infile)
        for index, data in enumerate(datas):
            try:
                tmp_dict = {}
                tmp_dict[K_id] = '{}_{}'.format(json_filename, index)
                tmp_dict[K_title_row] = data['title']
                tmp_dict[K_content_row] = data['blog']
                tmp_dict[K_content] = ' '.join(data['mecab'])
                tmp_dict[K_title] = \
                    ' '.join([token.surface 
                              for token 
                              in t.tokenize(tmp_dict[K_title_row])])
                ret_list.append(tmp_dict)
            except:
                _logger.error('cannot parse {}th data in {}'.format(
                    index,
                    json_filename))
    return ret_list

def register_all_blog_data_at(dir_path, whoosh_index):
    for filepath in tools.get_all_filename_at(dir_path, 'txt', 0):
        _logger.debug('registering {}'.format(filepath))
        data_list = parse_blog_data(filepath)
        register_data(data_list, whoosh_index)
    return whoosh_index

def regblog_main(args):
    _logger.debug('loading blog data from {} and register to {}'.format(
        args.path,
        args.index_dir))
    ix = search_archives.get_whoosh_index(args.index_dir)
    register_all_blog_data_at(args.path, ix)

def parse_mainichi_data(sgml_filepath, encoding='euc_jp'):
    ret_list = []
    with open(sgml_filepath, 'r', encoding=encoding) as infile:
        news_data = infile.read()
    for i, match in enumerate(doc_pat.finditer(news_data)):
        try:
            document = match.group(0)
            title = headline_pat.search(document).group(1)
            body = maintext_pat.search(document).group(1)
            tmp_dict = {}
            tmp_dict[K_id] = '{}_{}'.format(sgml_filepath, i)
            tmp_dict[K_title_row] = title
            tmp_dict[K_content_row] = body
            tmp_dict[K_title] = \
                ' '.join([token.surface
                          for token
                          in t.tokenize(tmp_dict[K_title_row])])
            tmp_dict[K_content] = \
                ' '.join([token.surface
                          for token
                          in t.tokenize(tmp_dict[K_content_row])])
            ret_list.append(tmp_dict)
        except:
            _logger.error('cannot parse {}th data in {}'.format(
                i,
                sgml_filepath))
    return ret_list

def register_all_mainichi_data_at(dir_path, whoosh_index):
    for filepath in tools.get_all_filename_at(dir_path, 'sgml', 1):
        _logger.debug('registering {}'.format(filepath))
        data_list = parse_mainichi_data(filepath)
        register_data(data_list, whoosh_index)
    return whoosh_index

def regmainichi_main(args):
    _logger.debug('loading newspaper data of mainichi from {} and '\
                  'register to {}'.format(args.path,
                                          args.index_dir))
    ix = search_archives.get_whoosh_index(args.index_dir)
    register_all_mainichi_data_at(args.path, ix)


def main(args):
    raise NotImplementedError

def set_parser():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-d', '--debug',
                        action='store_true',
                        default=False,
                        help='set debug mode (default:False)')
    parser.set_defaults(func=main)
    
    parser.add_argument('-i', '--index-dir',
                        dest='index_dir',
                        action='store',
                        type=str,
                        default=search_archives.DEF_index_dir,
                        metavar='DIRPATH',
                        help='set index directory path (default: {})'\
                             ''.format(search_archives.DEF_index_dir))
    
    parser.add_argument('-l', '--log-to',
                        dest='log_to',
                        action='store',
                        type=str,
                        default=None,
                        nargs='?',
                        const=DEF_log_filename,
                        metavar='FILENAME',
                        help='output log to FILENAME. if option setted but '\
                             'no FILENAME given, log to {} '\
                             '(default: no logging to file)'\
                             ''.format(DEF_log_filename))
    
    subparsers = parser.add_subparsers(help='subcommands', dest='command_name')
    
    parser_regblog = subparsers.add_parser('regblog', help='register blog datas')
    parser_regblog.set_defaults(func=regblog_main)
    parser_regblog.add_argument('path',
                                action='store',
                                type=str,
                                metavar='DIRPATH',
                                help='set path to blog data directory')
    
    parser_regmainichi = subparsers.add_parser(
        'regmainichi', 
        help='register mainichi newspaper datas')
    parser_regmainichi.set_defaults(func=regmainichi_main)
    parser_regmainichi.add_argument(
        'path',
        action='store',
        type=str,
        metavar='DIRPATH',
        help='set path to mainichi newspaper data directory')
    
    return parser

def enable_debug_mode():
    _basic_handler.setLevel(logging.DEBUG)
    _logger.info('debug mode enabled')
    global g_flg_debug
    g_flg_debug = True

if __name__ == '__main__':
    parser = set_parser()
    if '--test-mode' in sys.argv:
        import ignored_codes
        ignored_codes.register_entry()
        sys.exit()
    args = parser.parse_args()
    if args.debug:
        enable_debug_mode()
    if args.log_to != None:
        set_file_logger(args.log_to)
    args.func(args)