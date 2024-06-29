import gzip
import zlib
import re
from http.client import HTTPMessage

def with_color(c: int, s: str):
    return "\x1b[%dm%s\x1b[0m" % (c, s)

def filter_headers(headers: HTTPMessage) -> HTTPMessage:
    hop_by_hop = (
        "connection",
        "keep-alive",
        "proxy-authenticate",
        "proxy-authorization",
        "te",
        "trailers",
        "transfer-encoding",
        "upgrade",
    )
    for k in hop_by_hop:
        del headers[k]

    if "Accept-Encoding" in headers:
        ae = headers["Accept-Encoding"]
        filtered_encodings = [
            x for x in re.split(r",\s*", ae) if x in ("identity", "gzip", "x-gzip", "deflate")
        ]
        headers["Accept-Encoding"] = ", ".join(filtered_encodings)

    return headers

def encode_content_body(text: bytes, encoding: str) -> bytes:
    if encoding == "identity":
        data = text
    elif encoding in ("gzip", "x-gzip"):
        data = gzip.compress(text)
    elif encoding == "deflate":
        data = zlib.compress(text)
    else:
        raise Exception("Unknown Content-Encoding: %s" % encoding)
    return data

def decode_content_body(data: bytes, encoding: str) -> bytes:
    if encoding == "identity":
        text = data
    elif encoding in ("gzip", "x-gzip"):
        text = gzip.decompress(data)
    elif encoding == "deflate":
        try:
            text = zlib.decompress(data)
        except zlib.error:
            text = zlib.decompress(data, -zlib.MAX_WBITS)
    else:
        raise Exception("Unknown Content-Encoding: %s" % encoding)
    return text