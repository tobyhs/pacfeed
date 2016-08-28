import subprocess


class Package(object):
    """Metadata on a Pacman package."""

    def __init__(self, name, version):
        """
        Args:
            name: package name
            version: package version (including release number) (e.g. "1.2-3")
        """
        self.name = name
        self.version = version

    def __eq__(self, other):
        return (isinstance(other, Package) and
            self.name == other.name and self.version == other.version)

    def __repr__(self):
        class_ = self.__class__
        return '<%s.%s %s version=%s>' % (
            class_.__module__, class_.__qualname__, self.name, self.version
        )


class LocalPackageSet(object):
    """Collection for metadata on installed packages."""

    def __init__(self):
        output = subprocess.run(
            ['pacman', '-Q'], stdout=subprocess.PIPE, check=True
        ).stdout.decode()
        packages = output.split('\n')
        packages.pop() # Remove extra empty string due to trailing newline
        self.packages = {}
        for p in packages:
            p = p.split()
            self.packages[p[0]] = Package(p[0], p[1])

    def get(self, package_name):
        """Get metadata on the package with the given name.

        Args:
            package_name: name of package to retrieve metadata for

        Returns:
            A Package object if the package is installed, or None if the
            package is not installed.
        """
        return self.packages.get(package_name)
