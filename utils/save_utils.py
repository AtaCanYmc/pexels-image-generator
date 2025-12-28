import requests


def get_remote_size(url: str) -> dict:
    try:
        head = requests.head(url, timeout=10)
        cl = head.headers.get('Content-Length')
        if cl:
            size_bytes = int(cl)
            return {
                'bytes': size_bytes,
                'kb_decimal': size_bytes / 1000,
                'kb_binary': size_bytes / 1024,
                'source': 'Content-Length header'
            }
    except Exception:
        pass

    # Fallback: stream ile indirirken byte say (belleğe almadan)
    size = 0
    with requests.get(url, stream=True, timeout=30) as r:
        r.raise_for_status()
        for chunk in r.iter_content(8192):
            if chunk:
                size += len(chunk)

    return {
        'bytes': size,
        'kb_decimal': size / 1000 if size > 0 else 0,
        'kb_binary': size / 1024 if size > 0 else 0,
        'source': 'streamed download'
    }
