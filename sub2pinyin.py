# -*- coding: utf-8 -*-
import requests
import re
import multiprocessing
from tqdm import *
p = re.compile("[1-9][0-9]*\n.*-->.*\n")

headers = {
    'Host': 'translate.yandex.net',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Referer': 'https://translate.yandex.com/?lang=ru-zh&text=%E6%9C%AC%E6%9D%A5%E4%BB%8A%E5%A4%A9%E5%BA%94%E8%AF%A5%E6%98%AF%E6%88%91%E6%9D%A5%E5%8F%AB%E6%82%A8%E7%AC%AC%E4%B8%80%E5%A3%B0%E5%A6%88',
    'Origin': 'https://translate.yandex.com',
    'Connection': 'keep-alive',
}


def get_translit(text):
    data = [
      ('lang', 'zh'),
      ('text', text),
    ]
    r = requests.post('https://translate.yandex.net/translit/translit',
                      headers=headers, data=data)

    return r.text[1:-1].capitalize()

meta = []
translit = []
lines = []

with open('sub.srt') as srt:
    text = srt.read()
    print('Getting original text lines ...')
    lines = p.split(text)[1:]
    print('Getting meta data ...')
    meta = p.findall(text)

    pool = multiprocessing.Pool(processes=3)

    print('Translitterating using {}...'.format('Yandex'))

    with tqdm(total=len(lines)) as pbar:
        for i, _ in tqdm(enumerate(pool.imap(get_translit, lines))):
            translit.append(_)
            pbar.update()

    pbar.close()
    pool.close()
    pool.join()

    print('Recreating subtitle file ...')
if len(meta) != len(translit) != len(lines):
    print('Warning, the length of the different array don\'t match. Exiting...')
    print(len(meta))
    print(len(translit))
    print(len(lines))
else:
    res = zip(meta, translit, lines)
    res = map(lambda x: dict({'meta': x[0], 'translit': x[1], 'line': x[2]}),
              res)

    final_file = u''
    for sub in list(res):
        final_file += '{0}{1}\n{2}'.format(sub['meta'],
                                           sub['translit'],
                                           sub['line'])

    print('Writing to disk translitterated subtitle')
    with open('result.srt', 'w') as out:
        out.write(final_file)
