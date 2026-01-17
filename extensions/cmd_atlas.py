import logging
import subprocess

from pathlib import Path
from conan.api.conan_api import ConanAPI, ProfilesAPI, ConfigAPI
from conan.api.model import Remote
from conan.errors import ConanException
from conan.cli.command import conan_command, conan_subcommand
from conan.api.conan_api import ConanAPI
from conan.cli.command import conan_command

logger = logging.getLogger(__name__)

@conan_subcommand()
def atlas_setup(conan_api: ConanAPI, parser, subparser, *args):
    """
    Handles Conan Setup
    """
    

@conan_command(group="engine3d-dev")
def atlas(conan_api, parser, *args):
    """
    This is the help text for my custom command.
    """
    print("Hello this is calling from my custom command!")