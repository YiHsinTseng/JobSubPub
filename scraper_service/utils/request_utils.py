import requests
import time
import functools  # 缺少這一行，需補上

"""統一處理429、連線失敗、連線超時過久"""


def retry_on_429(max_retry=2, default_wait=5):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            retry_count = 0
            last_exception = None
            while retry_count <= max_retry:
                try:
                    return func(*args, **kwargs)  # 嘗試執行目標函數
                except requests.exceptions.HTTPError as e:
                    last_exception = e
                    retry_after = int(
                        e.response.headers.get("Retry-After", default_wait)
                    )
                    retry_count += 1
                    if e.response.status_code == 429:
                        print(
                            f"[HTTP 429] 第 {retry_count} 次重試，等待 {retry_after} 秒..."
                        )
                    else:
                        print(
                            f"[HTTP Error] 第 {retry_count} 次重試，等待 {retry_after} 秒..."
                        )
                    time.sleep(retry_after)
                except (
                    requests.exceptions.ConnectionError,
                    requests.exceptions.Timeout,
                ) as e:
                    last_exception = e
                    retry_count += 1
                    wait_time = default_wait
                    print(
                        f"[連線/超時錯誤] 第 {retry_count} 次重試，等待 {wait_time} 秒..."
                    )
                    time.sleep(wait_time)
                except Exception as e:
                    last_exception = e
                    print(f"[其他錯誤] {e}")
                    raise
            print(f"[錯誤] 超過最大重試次數({max_retry})，放棄執行。")
            if last_exception is not None:
                raise last_exception  # 只有當 last_exception 存在時才拋出

        return wrapper

    return decorator


@retry_on_429(max_retry=2, default_wait=1)
def make_request(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36",
        "Referer": url,
    }
    # 如果中斷會阻塞，記得替request 設定timeout
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()  # 確保拋出 HTTPError
    return response


@retry_on_429(max_retry=2, default_wait=1)
def make_job_request(url):
    check_url = url
    if url.startswith("https://www.104.com.tw/job/"):
        job_id = url.split("/")[-1]
        url = f"https://www.104.com.tw/job/ajax/content/{job_id}"
        check_url = f"https://www.104.com.tw/job/{job_id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36",
        "Referer": url,
    }
    time.sleep(0.0005)  # 這裡延遲極短，實際效果不明顯
    # 如果中斷會阻塞，記得替request 設定timeouts
    r = requests.get(url, headers=headers, timeout=10)
    r.raise_for_status()
    # print("Response status code:", r.status_code, url, "Check:", check_url)
    return r
