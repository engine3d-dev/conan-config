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

# @conan_subcommand()
# def atlas_build(conan_api: ConanAPI, parser, subparser, *args):
#     """
#     Automating build for Windows, Linux, and Mac Armv8 Builds
#     Usage: Conan atlas . build
#     """
#     subparser.add_argument(
#         "path", 
#         help="Path to the folder containing conanfile.py",
#         default=".",
#         nargs="?" # Makes the path optional, defaults to current directory
#     )

#     # Parse the arguments
#     info, _ = parser.parse_known_args(*args)

#     source_path = os.path.abspath(info.path)
#     if not os.path.exists(os.path.join(source_path, "conanfile.py")):
#         logger.error(f"❌ No conanfile found at: {source_path}")
#         return

#     # 3. Detect Platform-Specific Logic
#     os_name = platform.system()
#     arch = platform.machine().lower()
    
#     build_profile = "default"
#     confs = {}

#     os_name = platform.system()
#     arch = platform.machine().lower()
    
#     build_profile = "default"
#     confs = {}

#     if os_name == "Windows":
#         build_profile = "windows_x86_64"
#     elif os_name == "Linux":
#         build_profile = "linux_x86_64"
#         confs["tools.system.package_manager:sudo"] = True
#         confs["tools.system.package_manager:mode"] = "install"
#     elif os_name == "Darwin": # Mac
#         build_profile = "mac_armv8" if ("arm" in arch or "aarch64" in arch) else "mac_x86_64"

#     logger.info(f"🚀 Building project at: {source_path}")
#     logger.info(f"🛠️ Using profile: {build_profile}")

#     try:
#         # 4. Configure Profiles and Settings
#         profile_host = conan_api.profiles.get_profile([build_profile])
#         profile_build = conan_api.profiles.get_default_build()
        
#         # Set Debug mode
#         profile_host.settings["build_type"] = "Debug"
        
#         # Apply configurations (especially for Linux sudo)
#         for key, value in confs.items():
#             profile_host.conf.update(key, value)

#         # If we get an error to run
#         # Essentially adding a -b missing to build if there is an error that occurs with building the project.
#         # This resolves dependencies and generates build files
#         # conan_api.install.common(
#         #     path=source_path,
#         #     profiles=[profile_host, profile_build],
#         #     build=["missing"]
#         # )
        
#         # # This executes the actual 'build()' method in the conanfile
#         # conan_api.local.build(source_path)

#         # print(f"source_path = {source_path}")
#         # conan = ConanFile()
#         app = ConanApp(conan_api)
#         conanfile_path = conan_api.local.get_conanfile_path(source_path, os.getcwd(), True)
#         conanfile_obj = app.loader.load_consumer(conanfile_path)
#         conanfile_obj.folders.set_base_source(source_path)
#         conanfile_obj.folders.set_base_build(os.path.join(source_path, "build"))
#         conan_api.local.build(conanfile=conanfile_obj)
        
#         logger.info(f"✅ Successfully built {source_path}")
#     except Exception as e:
#         logger.error(f"❌ Build failed: {e}")

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
    
    # Since 'args' is now a list of strings (e.g., ['.', '--release']), 
    # unpacking it with *args works perfectly.
    parsed_args, conanfile_dir = subparser.parse_known_args(*args)
    
    build_type = "Release" if parsed_args.release else "Debug"
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