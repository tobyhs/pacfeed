import platform
import sys
import urllib.request
import xml.etree.ElementTree

from pacfeed import pacman


FEED_URL = 'https://www.archlinux.org/feeds/packages/%s/' % platform.machine()
# TODO: derive this from /etc/pacman.conf
REPOS = ('Core', 'Extra', 'Community')


def parse(handler):
    """Download packages feed and pass packages to the given handler.

    Args:
        handler: object to handle each package and pub_date
    """
    with urllib.request.urlopen(FEED_URL) as response:
        rss = xml.etree.ElementTree.parse(response)

    for item in rss.iter('item'):
        if item.find('category').text in REPOS:
            name, version = item.find('title').text.split()[0:2]
            package = pacman.Package(name, version)
            pub_date = item.find('pubDate').text
            handler.handle(package, pub_date)


class OutputHandler(object):
    """Class to print packages."""

    def __init__(self, output=sys.stdout):
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

        self.output.write('{}\033[30G {}'.format(package.name, package.version))
        self.output.write('\033[45G {}\033[0m\n'.format(pub_date))