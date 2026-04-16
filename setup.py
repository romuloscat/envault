"""Package setup for envault."""

from setuptools import setup, find_packages

setup(
    name="envault",
    version="0.1.0",
    description="A CLI tool to manage and encrypt environment variables across multiple projects.",
    author="envault contributors",
    python_requires=">=3.8",
    packages=find_packages(exclude=["tests*"]),
    install_requires=[
        "click>=8.0",
        "cryptography>=41.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov",
        ]
    },
    entry_points={
        "console_scripts": [
            "envault=envault.cli:cli",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Topic :: Security :: Cryptography",
        "Topic :: Utilities",
    ],
)
