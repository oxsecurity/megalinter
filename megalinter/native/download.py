import hashlib
import logging
import os
import ssl
import tempfile
import urllib.request
from urllib.parse import urlparse

from megalinter.native.context import NativeError

CHUNK_SIZE = 256 * 1024
USER_AGENT = "megalinter-native-installer"
TIMEOUT_SECONDS = 60


class HttpsOnlyRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if urlparse(newurl).scheme != "https":
            raise NativeError(f"Refusing redirect to a non-HTTPS URL: {newurl}")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def build_opener():
    context = ssl.create_default_context()
    return urllib.request.build_opener(
        urllib.request.HTTPSHandler(context=context), HttpsOnlyRedirectHandler()
    )


def sha256_of_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(CHUNK_SIZE), b""):
            digest.update(chunk)
    return digest.hexdigest()


def check_https(url):
    if urlparse(url).scheme != "https":
        raise NativeError(f"Refusing to download from a non-HTTPS URL: {url}")


def fetch_verified(url, sha256, size, cache_folder, offline=False, opener=None):
    check_https(url)
    sha256 = sha256.lower()
    os.makedirs(cache_folder, exist_ok=True)
    cached = os.path.join(cache_folder, sha256)
    if os.path.isfile(cached) and sha256_of_file(cached) == sha256:
        logging.debug(f"[native] cache hit {url}")
        return cached
    if offline:
        raise NativeError(f"NATIVE_OFFLINE is true and {url} is not in the cache")
    opener = opener or build_opener()
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    digest = hashlib.sha256()
    received = 0
    handle, temp_path = tempfile.mkstemp(dir=cache_folder, suffix=".part")
    try:
        with (
            os.fdopen(handle, "wb") as out,
            opener.open(request, timeout=TIMEOUT_SECONDS) as response,
        ):
            while True:
                chunk = response.read(CHUNK_SIZE)
                if not chunk:
                    break
                received += len(chunk)
                if size is not None and received > size:
                    raise NativeError(
                        f"{url} is larger than the {size} bytes recorded in the lock"
                    )
                digest.update(chunk)
                out.write(chunk)
        if size is not None and received != size:
            raise NativeError(
                f"{url} has {received} bytes, the lock records {size} bytes"
            )
        if digest.hexdigest() != sha256:
            raise NativeError(
                f"sha256 mismatch for {url}: expected {sha256}, got {digest.hexdigest()}"
            )
        os.replace(temp_path, cached)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
    return cached
