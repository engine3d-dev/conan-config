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
    Handle basic conan remote setup for TheAtlasEngine

    Command Example Usage:
    conan atlas setup
    """
    logger.info("Setting up TheAtlasEngine environment")

    # arguments that is used within the conan rmeote add <name_here> <url_here> commands
    REPO_URLS = ["https://libhal.jfrog.io/artifactory/api/conan/engine3d-conan", "https://libhal.jfrog.io/artifactory/api/conan/trunk-conan"]
    REPO_NAMES = ["engine3d-conan", "libhal-trunk"]

    def remote_exists(conan_api: ConanAPI, remote_name: str):
        try:
            conan_api.remotes.get(remote_name)
            return True
        except Exception:
            return False

    """
    Ensures the conan remotes are added
    """
    for (name, url) in zip(REPO_NAMES, REPO_URLS):
        try:
            if remote_exists(conan_api, name):
                logger.info(f"✅ Remote {name} already exists")
            else:
                logger.info(f"'{name}' does not exist, adding...")
                conan_api.remotes.add(Remote(name, url))
                logger.info(f"✅ Remote '{name}' was added successfully")
        except Exception as e:
            logger.error(f"❌ Failed to configure with remote {e}")
            return
        

    # Ensuring the conan host profiles are setup

    try:
        conan_api.profiles.get_default_host()
        logger.info("✅ System currently already have a default host profile, proceeding!")
        home_path = Path(conan_api.home_folder)
        default_profile_path = home_path / "profiles" / "default"
        detected_profile_info = conan_api.profiles.detect()
    except ConanException:
        logger.info("❌ Default host profile was not found! Generating one now...")
        home_path = Path(conan_api.home_folder)
        default_profile_path = home_path / "profiles" / "default"
        detected_profile_info = conan_api.profiles.detect()
        # logger.info(f"Home Path: {home_path}")
        # logger.info(f"Default Profile Path {default_profile_path}")
        # logger.info(f"Defalt Detected Profile: {detected_profile_info}")
        default_profile_path.write_text(str(detected_profile_info))
        logger.info("✅ Default profile generated!")
        logger.info(f"🔍 Profile Contents:\n{detected_profile_info}")

    logger.info("✅ TheAtlasEngine development environment setup is COMPLETE! 🚀")


@conan_command(group="engine3d-dev")
def atlas(conan_api, parser, *args):
    """
    TheAtlasEngine development tooling
    """
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    parser.add_argument(
        '--version',
        action='version',
        version='conan-config2: 1.1.1',
        help='Show version and exit'
    )

    parser.epilog = """
    Examples:
    conan atlas setup
    conan atlas update

    Use "conan atlas <command> --help" for more information on a specific command.
    """

    # Parse args to get verbose flag
    parsed_args, _ = parser.parse_known_args(*args)

    # Configure logging based on verbose flag
    log_level = logging.DEBUG if parsed_args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(message)s',
        force=True
    )