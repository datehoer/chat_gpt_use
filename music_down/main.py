import requests
import parsel
import time
import random
import urllib.parse
proxies = [
    {
        "http": "http://10.20.1.14:7891",
        "https": "http://10.20.1.14:7891"
    }, {
        "http": "http://10.20.1.14:7893",
        "https": "http://10.20.1.14:7893"
    }, {
        "http": "http://10.20.1.14:7895",
        "https": "http://10.20.1.14:7895"
    }
]

search_url = "https://www.gequbao.com/s/{}"

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "referer": "https://www.gequbao.com/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
}


def download(url, name, file_path):
    response = get_response(url)
    if response.status_code != 200:
        print('请求失败')
        return
    with open(file_path + name, 'wb') as f:
        f.write(response.content)


def get_music(url, file_path, need_lyric=False):
    response = get_response(url)
    if response.status_code != 200:
        print('请求失败')
        return
    selector = parsel.Selector(response.text)
    title = selector.css('.aplayer-title::text').get()
    music_download_link = selector.css('#btn-download-mp3::attr(href)').get()
    # 歌词
    music_download_lyric = selector.css('#btn-download-lrc::attr(href)').getall()
    # download
    download(music_download_link, title + '.mp3', file_path)
    if need_lyric:
        download(music_download_lyric, title + '.lrc', file_path)
    return "ok"


def analyze_result(result):
    selector = parsel.Selector(result)
    search_status = selector.css('.alert-danger *::text').getall()
    if search_status:
        search_status = ''.join(search_status)
        return search_status
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
    res = get_search_result(key_word)
    print(res)