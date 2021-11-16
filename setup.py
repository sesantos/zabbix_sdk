import sys
from setuptools import setup, find_packages

# we only support Python 3 version >= 3.4
#if len(sys.argv) >= 2 and sys.argv[1] == "install" and sys.version_info < (3, 4):
#    raise SystemExit("Python 3.4 or higher is required")


dependencies = open("requirements.txt", "r").read().splitlines()
setup(
    name="Zabbix Template Config Import",
    description="Imports Zabbix SRLinux Template, creates discovery rules and discovery actions",
    version="1.0",
    author="Sergio Santos",
    author_email="sergio.santos@nokia.com",
    install_requires=dependencies,
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "zabbix_setup_srlinux_env = setup_srlinux_env.zabbix_setup_srlinux_env:main",
        ]
    },
    platforms="any",
)