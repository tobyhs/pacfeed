import unittest
from unittest import mock

from pacfeed import pacman


class PackageTest(unittest.TestCase):
    def setUp(self):
        self.package = pacman.Package('python', '3.5.1-1')

    def test_name(self):
        self.assertEqual(self.package.name, 'python')

    def test_version(self):
        self.assertEqual(self.package.version, '3.5.1-1')

    def test_eq_true(self):
        self.assertEqual(self.package, pacman.Package('python', '3.5.1-1'))

    def test_eq_false(self):
        self.assertNotEqual(self.package, pacman.Package('python', '3.5.0-2'))
        self.assertNotEqual(self.package, pacman.Package('linux', '3.5.1-1'))

    def test_repr(self):
        self.assertEqual(
            repr(self.package),
            '<pacfeed.pacman.Package python version=3.5.1-1>'
        )


class LocalPackageSetTest(unittest.TestCase):
    def setUp(self):
        completed_process_mock = mock.Mock()
        completed_process_mock.stdout = b'coreutils 8.24-1\nlinux 4.3.3-2\npacman 4.2.1-4\n'
        run_mock = mock.patch('pacfeed.pacman.subprocess.run').start()
        run_mock.return_value = completed_process_mock
        self.addCleanup(mock.patch.stopall)

        self.local_package_set = pacman.LocalPackageSet()
        run_mock.assert_called_with(
            ['pacman', '-Q'], stdout=pacman.subprocess.PIPE, check=True
        )

    def test_get_with_installed_package(self):
        self.assertEqual(
            self.local_package_set.get('linux'),
            pacman.Package('linux', '4.3.3-2')
        )

    def test_get_with_not_installed_package(self):
        self.assertIsNone(self.local_package_set.get('foo'))
