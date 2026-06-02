"""Setup configuration for CleanText-CLI.

Installs the 'cleantext' console command and all package modules.
Zero external dependencies -- uses only Python standard library.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="cleantext-cli",
    version="1.0.0",
    description="Lightweight terminal AI text style purification engine",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="CleanText Contributors",
    license="MIT",
    python_requires=">=3.7",
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "cleantext=cleantext_cli.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Text Processing",
        "Topic :: Utilities",
    ],
)
