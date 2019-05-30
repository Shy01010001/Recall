#encoding: utf8
'''
Created on 2019/05/17

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

_g_flg_debug = False

import search_archives as sa

def search_and_get_leading_sentence(sentence,                                 
                                    top_n=sa.DEF_top_n,
                                    index_dir='/home/godl/Desktop/slack-new/indexdir',
                                    query_function=sa.extract_contents_words):
    results = sa.search_index_by_sentence(sentence, 
                                          top_n, 
                                          index_dir, 
                                          query_function)
    leading_sentences = []
    for result in results:
        leading_line = result['content'].strip().splitlines()[0]
        leading_sentence = leading_line.split('。．　')[0]
        leading_sentences.append(leading_sentence)
    return leading_sentences

def main(args):
    raise NotImplementedError

def set_parser():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-d', '--debug',
                        action='store_true',
                        default=False,
                        help='set debug mode (default:False)')
    parser.set_defaults(func=main)
    return parser

def enable_debug_mode():
    _logger.setLevel(logging.DEBUG)
    _logger.info('debug mode enabled')
    global g_flg_debug
    g_flg_debug = True

if __name__ == '__main__':
    parser = set_parser()
    if '--test-mode' in sys.argv:
        import ignored_codes
        ignored_codes.wrapper_for_slackbot()
        sys.exit()
    args = parser.parse_args()
    if args.debug:
        enable_debug_mode()
    args.func(args)