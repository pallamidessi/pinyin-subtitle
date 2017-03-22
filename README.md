# pinyin-subtitle
A small tool to create a subtitle with Pinyin translitteration from chinese (mandarin) subtitle 

## Requirements:
Python > 3

## Installation:
```
pip install -r requirements.txt
```

## Usage: 
```
Usage: sub2pinyin.py [-h] [-l LANG] [-w WORKERS] input_file [output_file]
```
By default the script will translitterate chinese using Yandex's unofficial API.

## Example:
Original (left) vs pinyinificated (right):

original | pinyinificated
--------:|:-------------- 
![zh](https://raw.githubusercontent.com/pallamidessi/pinyin-subtitle/master/examples/yiyi1.png) | ![zh-pinyin](https://raw.githubusercontent.com/pallamidessi/pinyin-subtitle/master/examples/yiyi2.png)

## Multiple subtitle
To get multiple subtitle, at the top and bottom at the same time with mpv (with
english on auto-load, i.e: example.srt in current folder):
```
mpv example.mkv --sid=auto --sub-file=/path/to/chinese-pinyin.srt --secondary-sid=1
```
![zh-pinyin-eng](https://raw.githubusercontent.com/pallamidessi/pinyin-subtitle/master/examples/yiyi.png)

## Future developements
* Create yandex-translit module
* Use Advanced Subtitle Styling (.ass) for specific styling and muxing of external
  subtitle

## Credits
All screenshot are from Edward Yang's Yi Yi:
* [Edward Wang's Wikipedia page](https://en.wikipedia.org/wiki/Edward_Yang)
* [Yi Yi's Wikipedia page](https://en.wikipedia.org/wiki/Yi_Yi)

Transliteration API unofficialy provided by Yandex:
* [Yandex translate](https://translate.yandex.com/developers)
