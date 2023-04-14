# coding: utf-8
import requests
import parsel
import re
import random
import urllib.parse
proxies = [
    {
        "http": "http://127.0.0.1:7890",
        "https": "http://127.0.0.1:7890"
    }
]

search_url = "https://www.gequbao.com/s/{}"

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "referer": "https://www.gequbao.com/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
}


def download(url, file_path):
    response = get_response(url)
    if response.status_code != 200:
        print('请求失败')
        return
    with open(file_path, 'wb') as f:
        f.write(response.content)


def get_music(url, music_path, lyric_path=None):
    response = get_response(url)
    if response.status_code != 200:
        print('请求失败')
        return
    selector = parsel.Selector(response.content.decode("utf-8"))
    music_download_link = selector.css('script').getall()
    music_download_link = [item for item in music_download_link if "const url = '" in item]
    if music_download_link:
        music_download_link = re.findall(r"const url = \'(.*)\'\.r", music_download_link[0])[0]
    # 歌词
    music_download_lyric = selector.css('#btn-download-lrc::attr(href)').get()
    if music_download_lyric is not None and not music_download_lyric.startswith('http'):
        music_download_lyric = 'https://www.gequbao.com' + music_download_lyric
    if music_download_link != "kuwo.cn":
        if music_path:
            download(music_download_link, music_path)
        if lyric_path:
            download(music_download_lyric, lyric_path)
        return True
    return False


def analyze_result(result):
    selector = parsel.Selector(result)
    search_status = selector.css('.alert-danger *::text').getall()
    if search_status:
        return None
    search_count = selector.css('span~small::text').get()
    search_result = selector.css('div.card-text tbody tr')
    result = []
    for item in search_result:
        title = item.css('td:nth-child(1) a::text').get()
        link = item.css('td:nth-child(1) a::attr(href)').get()
        if link is not None and not link.startswith('http'):
            link = 'https://www.gequbao.com' + link
        author = item.css('td:nth-child(2)::text').get()
        result.append({
            'title': title,
            'link': link,
            'author': author,
        })
    return search_count, result


def get_response(url):
    response = requests.get(url, headers=headers, proxies=random.choice(proxies))
    return response


def get_search_result(keyword):
    url = search_url.format(urllib.parse.quote(keyword))
    response = get_response(url)
    if response.status_code != 200:
        print('请求失败')
        return
    result = analyze_result(response.text)
    return result


if __name__ == '__main__':
    key_word = '周杰伦'
    res = get_music('https://www.gequbao.com/music/112019', '周杰伦.mp3')
    print(res)