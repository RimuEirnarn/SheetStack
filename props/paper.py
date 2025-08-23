"""Paper related module"""

from os import remove
from os.path import exists
from json import loads
import time

from tqdm import tqdm
from requests import get, head

from props.typings import GlobalRepo, VersionBuildRepo
from .config import APP_CACHE_VAULT, SERVER_BIN

REPOSITORY = "https://api.papermc.io/v2/projects/paper"
VERSION_REPO = "https://api.papermc.io/v2/projects/paper/versions/{version}"
BUILDS_REPO = "https://api.papermc.io/v2/projects/paper/versions/{version}/builds/{build}/downloads/paper-{version}-{build}.jar"
GENERIC_FILE = "paper-{version}-{build}.jar"
ERR = {}

DEFAULT_CHUNK_SIZE = 16 * 1024

DEFAULT_TIMEOUT = 5
CACHE_TTL = 1 * (24 * 3600)


def fetch(url: str, name: str, force: bool = False):
    """Fetch current content and store to cache fault"""
    cache = APP_CACHE_VAULT / name
    if cache.exists() and force is False:
        if cache.stat().st_mtime >= (time.time() - CACHE_TTL):
            return loads(cache.read_text())
    data = get(url, timeout=5)
    if not data.ok:
        exc = ValueError(data.reason)
        err_store = f"cache_fault/{name}"
        exc.add_note(f"Data can be retrieved by using this key {err_store!r}")
        ERR[err_store] = data
        raise exc

    (APP_CACHE_VAULT / name).write_text(data.content.decode())
    return data.json()


def fetch_global() -> GlobalRepo:
    """Fetch global repository metadata"""
    return fetch(REPOSITORY, "repo.cache")


def fetch_version_info(version: str) -> VersionBuildRepo:
    """Fetch version info"""
    return fetch(VERSION_REPO.format(version=version), f"v{version}.cache")

def fetch_minecraft(version: str, build: int):
    """Fetch server jar"""
    url = BUILDS_REPO.format(version=version, build=build)
    filename = SERVER_BIN / GENERIC_FILE.format(version=version, build=build)
    header = head(url, timeout=DEFAULT_TIMEOUT)
    total_size = int(header.headers.get("content-length", 0))
    if exists(filename):
        print("This download will overwrite existing file")
        remove(filename)
    with get(url, stream=True, timeout=DEFAULT_TIMEOUT) as stream, open(filename, 'wb') as file:
        stream.raise_for_status()
        with tqdm(total=total_size, unit="B", unit_scale=True, desc="Downloading") as progress:
            for chunk in stream.iter_content(DEFAULT_CHUNK_SIZE):
                if chunk:
                    file.write(chunk)
                    progress.update(len(chunk))
