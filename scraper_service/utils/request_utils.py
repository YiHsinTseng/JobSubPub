import requests
import time

def make_request(url):
    if url.startswith('https://www.104.com.tw/job/'):
        job_id = url.split('/')[-1]
        url = f'https://www.104.com.tw/job/ajax/content/{job_id}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36',
        "Referer": url
    }
    time.sleep(0.0005)
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    print('Response status code:', r.status_code, url)
    return r