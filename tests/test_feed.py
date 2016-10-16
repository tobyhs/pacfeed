import io
import re
from os import path
import unittest
from unittest import mock

from pacfeed import feed
from pacfeed import pacman


class TestHandler(object):
    """Handler class to help test pacfeed.feed.parse."""

    def __init__(self):
        self.packages = []

    def handle(self, package, pub_date):
        """Add a package."""
        self.packages.append((package, pub_date))


class GetReposTest(unittest.TestCase):
    def test_get_repos(self):
        repos = feed.get_repos(path.dirname(__file__) + '/fixtures/pacman.conf')
        self.assertEqual(repos, ('Core', 'Extra'))


class ParseTest(unittest.TestCase):
    def test_parse(self):
        handler = TestHandler()
        fake_response = open(path.dirname(__file__) + '/fixtures/rss.xml')

        with mock.patch('pacfeed.feed.urllib.request.urlopen') as open_patch,\
                mock.patch('pacfeed.feed.get_repos') as get_repos_patch:
            get_repos_patch.return_value = ('Core', 'Extra')
            open_patch.return_value = fake_response
            feed.parse(handler)
            open_patch.assert_called_once_with(feed.FEED_URL)

        self.assertEqual(handler.packages, [
            (
                pacman.Package('libreoffice-fresh', '5.2.0-4'),
                'Sun, 28 Aug 2016 19:56:03 +0000'
            ),
            (
                pacman.Package('man-db', '2.7.5-4'),
                'Sun, 28 Aug 2016 01:57:45 +0000'
            ),
        ])


class OutputHandlerTest(unittest.TestCase):
    def setUp(self):
        self.output = io.StringIO()
        self.local_package_set = mock.create_autospec(pacman.LocalPackageSet)
        init_patch = mock.patch('pacfeed.feed.pacman.LocalPackageSet').start()
        self.addCleanup(mock.patch.stopall)
        init_patch.return_value = self.local_package_set

        self.handler = feed.OutputHandler(self.output)
        self.package = pacman.Package('foo', '1.2-3')
        self.pub_date = 'Tue, 19 Jan 2016 06:36:16 +0000'

    def test_handle_with_up_to_date_package(self):
        self._test_handle(self.package, '\033[92mfoo')

    def test_handle_with_out_of_date_package(self):
        newer_package = pacman.Package('foo', '1.3-1')
        self._test_handle(newer_package, '\033[91mfoo')

    def test_handle_with_uninstalled_package(self):
        self._test_handle(None, 'foo')

    def _test_handle(self, get_return_value, prefix):
        """Runs the common test for the handle method.

        Args:
           get_return_value: return value for the get method of the
               LocalPackageSet mock
           prefix: prefix string for matching against OutputHandler's output
        """
        self.local_package_set.get.return_value = get_return_value
        self.handler.handle(self.package, self.pub_date)
        self.local_package_set.get.assert_called_once_with(self.package.name)

        format_args = (self.package.name, self.package.version, self.pub_date)
        regex = '{}.*{}.*{}'.format(*(re.escape(s) for s in format_args))
        output = self.output.getvalue()

        self.assertTrue(output.startswith(prefix))
        self.assertRegex(output, regex)
        self.assertTrue(output.endswith('\033[0m\n'))
