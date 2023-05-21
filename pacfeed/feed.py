import configparser
import platform
import sys
import urllib.request
import xml.etree.ElementTree

from pacfeed import pacman


FEED_URL = f'https://www.archlinux.org/feeds/packages/{platform.machine()}/'


def get_repos(config_path='/etc/pacman.conf'):
    """Reads the Pacman configuration file to get the official repos enabled.

    Args:
        config_path: path to Pacman configuration file
    Returns:
        a tuple of repository names
    """
    config = configparser.ConfigParser(allow_no_value=True)
    config.read(config_path)
    sections = config.sections()
    return tuple(
        section.title() for section in sections
        if _is_official_repo(config, section)
    )

def _is_official_repo(config, section):
    include = config.get(section, 'Include', fallback=None)
    return include == '/etc/pacman.d/mirrorlist'

def parse(handler):
    """Download packages feed and pass packages to the given handler.

    Args:
        handler: object to handle each package and pub_date
    """
    repos = get_repos()
    with urllib.request.urlopen(FEED_URL) as response:
        rss = xml.etree.ElementTree.parse(response)

    for item in rss.iter('item'):
        if item.find('category').text in repos:
            name, version = item.find('title').text.split()[0:2]
            package = pacman.Package(name, version)
            pub_date = item.find('pubDate').text
            handler.handle(package, pub_date)


class OutputHandler(object):
    """Class to print packages."""

    def __init__(self, output=sys.stdout):
        """
        Args:
            output: object with a write method to write output to
        """
        self.output = output
        self.local_package_set = pacman.LocalPackageSet()

    def handle(self, package, pub_date):
        """Print the given package in the right color.

        Up-to-date packages are in green and out-of-date packages are in red.
        Packages not installed are in white.

        Args:
            package: pacfeed.pacman.Package object to handle
            pub_date: string of date when package was published
        """
        local_package = self.local_package_set.get(package.name)
        if local_package == package:
            self.output.write('\033[92m') # Green
        elif local_package:
            self.output.write('\033[91m') # Red

        self.output.write(f'{package.name}\033[30G {package.version}')
        self.output.write(f'\033[45G {pub_date}\033[0m\n')
