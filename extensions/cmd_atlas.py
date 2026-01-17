import logging
import subprocess
import platform

from pathlib import Path
from conan import ConanFile
from conan.api.conan_api import ConanAPI, ProfilesAPI, ConfigAPI
from conan.cli.cli import Cli
from conan.internal.conan_app import ConanApp
from conan.api.model import Remote
from conan.errors import ConanException
from conan.cli.command import conan_command, conan_subcommand
from conan.api.conan_api import ConanAPI
from conan.cli.command import conan_command
import os

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

@conan_subcommand()
def atlas_build(conan_api: ConanAPI, parser, subparser, *args):
    """
    Build the project with platform-specific defaults.
    """
    subparser.add_argument("--release", action="store_true", help="Build in Release mode")
    subparser.add_argument(
        "path", 
        nargs="?", 
        default=".", 
        help="Path to the recipe folder"
    )

    # For an example commands such as `conan atlas build .`
    # *args contain the following content (['build', '.'],)
    parsed_args, conanfile_dir = subparser.parse_known_args(*args)
    # logger.info(f"BUILD_TYPE = {parsed_args.release}")
    build_type = "Release" if parsed_args.release else "Debug"
    # 2. Handle Build Types dynamically
    # We use a list to define allowed types. This isn't 'hardcoding' logic;
    # it's defining the API's allowed schema.
    BUILD_TYPES = ["Debug", "Release", "MinSizeRel", "RelWithDebInfo"]
    
    # We add a single argument '--type' but allow users to pass the name.
    # Alternatively, we can create flags for each. 
    # Here is the most flexible way:
    subparser.add_argument(
        "--type",
        # aliases=["-t"],
        choices=BUILD_TYPES,
        default="Debug",
        help="Specify the build type (Debug, Release, etc.)"
    )
    # 3. Parse the *args
    # args[0] contains ['build', '.', '--type', 'Release']
    parsed_args, unknown_args = subparser.parse_known_args(*args)

    # 4. Retrieve the values
    # No if/else needed! The value is pulled directly from the input.
    test_type = parsed_args.type
    logger.info(f"TEST BUILD_TYPE = {test_type}")


    build_path = Path(parsed_args.path).resolve()
    
    # Platform detection logic
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    profile = ""
    confs = []

    if system == "windows":
        profile = "windows_x86_64"
    elif system == "darwin":
        profile = "mac_armv8" if "arm" in machine else "mac_x86_64"
    elif system == "linux":
        profile = "linux_x86_64"
        confs["tools.system.package_manager:sudo"] = True
        confs["tools.system.package_manager:mode"] = "install"

    # Build the command
    # logger.info(f"*args[0] = {args[0]}")
    logger.info(f"Current PATH = {conanfile_dir[0]}")
    cmd = [
        "conan", "build", str(conanfile_dir[0]),
        "-b", "missing",
        "-s", f"build_type={build_type}",
        "-pr", profile
    ]
    cmd.extend(confs)

    logger.info(f"🛠️ Building: {build_path} | Profile: {profile} | Mode: {build_type}")

    try:
        subprocess.run(cmd, check=True)
        logger.info("✅ Build completed successfully!")
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Build failed with exit code {e.returncode}")

@conan_command(group="engine3d-dev")
def atlas(conan_api, parser, *args):
    """
    TheAtlasEngine development tool
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