"""Typing modules"""
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

class Memory(TypedDict):
    """Memory configuration"""
    min: int
    max: int
class Config(TypedDict):
    """System configuration"""
    path: str
    java_path: str
    memory: Memory
    gui: bool
    additional_args: list[str]
