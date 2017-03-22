# -*- coding: utf-8 -*-
from sys import exit
from re import compile
from argparse import ArgumentParser
from multiprocessing import Pool

from colorama import Fore, Back, Style
from requests import post, exceptions
from tqdm import tqdm

DEBUG = False


def print_step(text):
    print(Fore.GREEN + text + '\n' + Style.RESET_ALL)


def print_summary(lang, input_file, output_file, api, workers):
    """Pretty print the script option and settings before launch"""
    print()
    print(Fore.RED + Back.WHITE +'Summary' + Style.RESET_ALL)
    print(Fore.RED + 'About to translit text with the following parameter:' + Style.RESET_ALL)
    print('Target language: {}{}{}'.format(Fore.GREEN, lang, Style.RESET_ALL))
    print('Input file: {}{}{}'.format(Fore.GREEN, input_file, Style.RESET_ALL))
    print('Output file: {}{}{}'.format(Fore.GREEN, output_file, Style.RESET_ALL))
    print('Selected API: {}{}{}'.format(Fore.GREEN, api, Style.RESET_ALL))
    print('Number of worker: {}{}{}'.format(Fore.GREEN, workers, Style.RESET_ALL))
    print()


class Translitterator(object):
    """Wrapper around translitteration API"""

    yandex_api_headers = {
        'Host': 'translate.yandex.net',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:45.0) Gecko/20100101\
            Firefox/45.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;\
            q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Referer': 'https://translate.yandex.com/?lang=ru-zh&text=0',
        'Origin': 'https://translate.yandex.com',
        'Connection': 'keep-alive',
    }

    def __init__(self, lang='zh', api='yandex'):
        super(Translitterator, self).__init__()
        self.api = api
        self.lang = lang

        if api == 'yandex':
            self.api_headers = Translitterator.yandex_api_headers

    def translit(self, text, lang=None):
        """Return translitteration of given text using language"""
        if lang is None:
            lang = self.lang

        if self.api == 'yandex':
            if len(text) > 100:
                print('WARNING: Yandex API doesn\'t support request of more than 100\
                       caracters')
        data = [
          ('lang', lang),
          ('text', text),
        ]

        try:
            r = post('https://translate.yandex.net/translit/translit',
                     headers=self.api_headers, data=data)
        except exceptions.RequestException as e:  # This is the correct syntax
            print(e)
            exit(1)

        # Remove additional double quote added by yandex translit api
        return r.text[1:-1].capitalize()

    def parallel_translit(self, texts, lang=None, nb_worker=3,
                          show_progress=True):
        """Return translitteration of a list of string in parallel using language
            Also display a progress bar that can be disable
        """
        if lang is None:
            lang = self.lang

        pool = Pool(processes=nb_worker)
        results = []

        if show_progress:
            with tqdm(total=len(lines)) as pbar:
                for i, _ in tqdm(enumerate(pool.imap(self.translit, lines))):
                    results.append(_)
                    pbar.update()

            pbar.close()
            pool.close()
            pool.join()
        else:
            results = map(self.translit, lines)

        return results


if __name__ == "__main__":
    parser = ArgumentParser(description='Translitteration of subtitle')

    parser.add_argument('-l', '--lang', help='Language of subtitle (i.e script used)')
    parser.add_argument('-w', '--workers', help='Number of worker to use (default 3)')
    parser.add_argument('input_file', help='Path of input subtitle file')
    parser.add_argument('output_file', nargs='?', help='Path of output file. If not described\
                        will append \'_result\' to input filename')

    args = parser.parse_args()

    if args.input_file is None:
        print(u'Usage: sub2pinyin.py [option] filename [output_filename]')
        exit(2)

    input_file = args.input_file

    if args.lang is None:
        lang = 'zh'
    else:
        lang = args.lang

    if args.workers is None:
        nb_worker = 3
    else:
        nb_worker = int(args.workers)

    if args.output_file is None:
        if input_file.find('.srt') != -1:
            output_file = input_file.replace('.srt', '_result.srt')
        else:
            output_file = input_file + '_result'

    api = 'yandex'
    print_summary(lang, input_file, output_file, api, nb_worker)

    with open(input_file) as srt:

        meta = []
        translit = []
        lines = []

        text = srt.read()

        # Regex to split srt file by line's timestamp metadata
        # i.e: y\n xx.xx.xxx --> xx.xx.xxx\n
        metadata_pattern = compile("[1-9][0-9]*\n.*-->.*\n")

        # Skip the first element, artefact of regex splitting (empty string '')
        print_step('[1/4] Extracting original text lines ...')
        lines = metadata_pattern.split(text)[1:]

        print_step('[2/4] Extracting metadata ...')
        meta = metadata_pattern.findall(text)

        print_step('[3/4] Translitterating using {}... \n\
                    It may take a while (> 10 minutes avg)'.format('Yandex'))
        translitterator = Translitterator(lang='zh')
        translit = translitterator.parallel_translit(lines, nb_worker=nb_worker)

        print_step('[4/4] Recreating subtitle file ...')

        # Basic check: if the different array don't match in size
        # (SoA principle)
        if len(meta) != len(translit) != len(lines):
            print('Warning, the length of the different array don\'t match.\
            Exiting...')
            if DEBUG:
                print(u'Meta array\'s length:{0}'.format(len(meta)))
                print(u'Translitteration array\'s length:{0}'.format(len(translit)))
                print(u'lines array\'s length:{0}'.format(len(lines)))
        else:
            transliterate_results = zip(meta, translit, lines)
            transliterate_results = map(lambda x: dict({'meta': x[0], 'translit': x[1], 'line': x[2]}),
                                        transliterate_results)

            translit_file_data = u''
            for sub in list(transliterate_results):
                translit_file_data += '{0}{1}\n{2}'.format(sub['meta'],
                                                           sub['translit'],
                                                           sub['line'])

            print('Writing to disk translitterated subtitle')
            with open(output_file, 'w') as out:
                out.write(translit_file_data)
