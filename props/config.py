"""General config"""

from pathlib import Path
from yaml import load, dump, SafeLoader

APP_DIR = Path("~/.server_mgr").expanduser()
APP_CACHE_VAULT = APP_DIR / "cache"
APP_CONFIG = APP_DIR / "config.yaml"
APP_DIR.mkdir(exist_ok=True)
APP_CACHE_VAULT.mkdir(exist_ok=True)

if not (APP_CONFIG).exists():
    read_path = input("Please type your designated server directory\n-> ")
    with open(APP_CONFIG, 'w', encoding='utf-8') as file:
        dump({'path': str(Path(read_path).absolute())}, file, indent=2)
else:
    with open(APP_CONFIG, encoding='utf-8') as file:
        config = load(file, SafeLoader)
    read_path = config['path']

SERVER_PATH = Path(read_path).absolute()
SERVER_BIN = SERVER_PATH / "bin"
PROFILE_DIR = SERVER_PATH / "profiles"
DEFAULT_SYMLINK = SERVER_PATH / "default" / "server.jar"
DEFAULT_PROFILE = SERVER_PATH / "default"

SERVER_PATH.mkdir(exist_ok=True)
SERVER_BIN.mkdir(exist_ok=True)
PROFILE_DIR.mkdir(exist_ok=True)
