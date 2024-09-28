import httpx

""" Init httpx client """
# 使用自定义 UA
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.72 Safari/537.36"
}
client = httpx.AsyncClient(timeout=10.0, headers=headers)
