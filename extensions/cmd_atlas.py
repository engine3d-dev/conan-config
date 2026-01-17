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
    parsed_args, conanfile_args = subparser.parse_known_args(*args)

    # We splice to extend the following commands to automatically directly be extended from the main commands call
    # Meaning if we have something like: `conan atlas build . -s build_type=Debug -o enable_tests_only=True`
    # We would parse pass `-s` and slice those following arguments directly with the commands to be executed as optional arguments specified.
    forward_args = conanfile_args[1:]

    # parsed_args handles your --release flag
    # conanfile_args[1:] captures everything like ['-s', 'build_type=RelWithDebInfo', '-o', ...]
    # parsed_args2, conanfile_args = subparser.parse_known_args(*args)
    forward_args2 = conanfile_args[1:] if len(conanfile_args) > 1 else []

    # We look for 'build_type=' in forward_args. If found, we take that value.
    # If NOT found, we check the --release flag.
    # If neither exists, we default to "Debug".
    extracted_build_type = next(
        (arg.split('=')[-1] for arg in forward_args2 if "build_type=" in arg),
        "Release" if parsed_args.release else "Debug"
    )

    build_path = Path(parsed_args.path).resolve()
    
    # Detecting host platform
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
        # confs["tools.system.package_manager:sudo"] = "True"
        # confs["tools.system.package_manager:mode"] = "install"
        confs.extend([
            "-c", "tools.system.package_manager:sudo=True",
            "-c", "tools.system.package_manager:mode=install"
        ])

    # Building thje accumulative commands to the final command output to execute.
    logger.info(f"Current PATH = {conanfile_args[0]}")
    cmd = [
        "conan", "build", str(conanfile_args[0]),
        "-b", "missing",
        "-s", f"build_type={extracted_build_type}",
        "-pr", profile
    ]
    cmd.extend(confs)
    cmd.extend(forward_args)

    logger.info(f"🛠️ Building: {build_path} | Profile: {profile} | Build Type: {extracted_build_type}")

    try:
        subprocess.run(cmd, check=True)
        logger.info("✅ Build completed successfully!")
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Build failed with exit code {e.returncode}")

@conan_subcommand()
def atlas_create(conan_api: ConanAPI, parser, subparser, *args):
    """
    Example Usage:
    conan atlas create . -s build_type=Debug
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
    parsed_args, conanfile_args = subparser.parse_known_args(*args)

    # We splice to extend the following commands to automatically directly be extended from the main commands call
    # Meaning if we have something like: `conan atlas build . -s build_type=Debug -o enable_tests_only=True`
    # We would parse pass `-s` and slice those following arguments directly with the commands to be executed as optional arguments specified.
    forward_args = conanfile_args[1:]

    # 2. Parse arguments
    # parsed_args handles your --release flag
    # conanfile_args[1:] captures everything like ['-s', 'build_type=RelWithDebInfo', '-o', ...]
    # parsed_args2, conanfile_args = subparser.parse_known_args(*args)
    forward_args2 = conanfile_args[1:] if len(conanfile_args) > 1 else []

    # We look for 'build_type=' in forward_args. If found, we take that value.
    extracted_build_type = next(
        (arg.split('=')[-1] for arg in forward_args2 if "build_type=" in arg),
        "Release" if parsed_args.release else "Debug"
    )

    build_path = Path(parsed_args.path).resolve()
    
    # Detecting host platform
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
        # confs["tools.system.package_manager:sudo"] = "True"
        # confs["tools.system.package_manager:mode"] = "install"
        confs.extend([
            "-c", "tools.system.package_manager:sudo=True",
            "-c", "tools.system.package_manager:mode=install"
        ])

    # Building thje accumulative commands to the final command output to execute.
    logger.info(f"Current PATH = {conanfile_args[0]}")
    cmd = [
        "conan", "create", str(conanfile_args[0]),
        "-b", "missing",
        "-s", f"build_type={extracted_build_type}",
        "-pr", profile
    ]
    cmd.extend(confs)
    cmd.extend(forward_args)

    logger.info(f"🛠️ Building: {build_path} | Profile: {profile} | Build Type: {extracted_build_type}")

    try:
        subprocess.run(cmd, check=True)
        logger.info("✅ Build completed successfully!")
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Build failed with exit code {e.returncode}")

@conan_command(group="engine3d-dev")
def atlas(conan_api, parser, *args):
    """
    TheAtlasEngine custom commands
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
    conan atlas build <path> <arguments>
    conan atlas create <path> <arguments>

    Use "conan atlas --help" for more information on a specific command.
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