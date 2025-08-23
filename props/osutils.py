import os
from .config import DEFAULT_SYMLINK, PROFILE_DIR
from .data import ReturnInfo, ReturnType

def list_versions(directory: str):
    """
    List all available PaperMC versions (JAR files) in the given directory.
    """
    if not os.path.exists(directory):
        return ReturnInfo(ReturnType.ERR, f"Directory '{directory}' does not exists", None)

    versions = [
        f for f in os.listdir(directory)
        if f.startswith("paper") and f.endswith(".jar")
    ]
    return ReturnInfo(ReturnType.OK, "", sorted(versions))


def get_active_version():
    """
    Determine which version is currently active based on the server.jar symlink.
    """
    if os.path.islink(DEFAULT_SYMLINK):
        target = os.readlink(DEFAULT_SYMLINK)
        return os.path.basename(target)
    return None


def create_profile(version: str) -> ReturnInfo[str]:
    """
    Ensure that an isolated profile directory exists for the selected version.
    """
    profile_path = os.path.join(PROFILE_DIR, version.replace(".jar", ""))
    if not os.path.exists(profile_path):
        os.makedirs(profile_path)
    return ReturnInfo(ReturnType.OK, f"Created profile directory: {profile_path}", profile_path)


def create_symlink(source: str, destination: str) -> ReturnInfo[None]:
    """
    Create or update the symlink for the default server.jar.
    """
    if os.path.islink(destination) or os.path.exists(destination):
        os.remove(destination)
    os.symlink(os.path.abspath(source), destination)
    return ReturnInfo(ReturnType.OK, f"Symlink updated from {destination} -> {source}", None)
