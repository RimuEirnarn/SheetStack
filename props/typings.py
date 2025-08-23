from typing import TypedDict

class GlobalRepo(TypedDict):
    """Global repository metadata"""
    project_id: str
    project_name: str
    version_groups: list[str]
    versions: list[str]

class VersionBuildRepo(TypedDict):
    """Version repository metadata"""
    project_id: str
    project_name: str
    version: str
    builds: list[int]
