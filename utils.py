import sys
from pathlib import Path


def resolve_path(resource_name):
    """
    Returns the full path to a resource (file) located in the same directory as the script or executable.

    :param resource_name: The name of the resource (file) to access (e.g., 'data.txt')
    :return: The absolute path to the resource
    """
    # Get the directory of the current script (whether running as a script or bundled executable)
    # Note: It will run from within the _internal directory, as utils.pyc
    # i.e. dist\main\_internal\utils.pyc when bundled
    if getattr(sys, 'frozen', False):
        base_path = Path(__file__).resolve().parent.parent
    else:
        base_path = Path(__file__).resolve().parent

    # Construct the full path to the resource
    resource_path = base_path / resource_name

    return resource_path

