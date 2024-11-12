from os import path
from setuptools import find_packages, setup


long_description = open("README.md", 'r').read() if path.exists('README.md') else ""

setup(
    name="scraby",
    version="0.0.0",
    author="Ivan Derkach",
    author_email="dsp_shp@icloud.com",
    description="Python scraping tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="Apache-2.0",
    license_files=("LICENSE.txt",),
    url="https://github.com/dsp-shp/scraby",
    packages=find_packages(exclude=["docs", "docs.*", "tests", "tests.*"]),
    package_data={"": ["examples/**"]},
    entry_points={
        "console_scripts": [
            "scraby = scraby.main:cli",
        ],
    },
    python_requires=">=3.7",
    install_requires=[
        "beautifulsoup4",
        "click",
        "duckdb",
        "pytest-playwright",
        "sqlglot==25.29.0",
    ],
    extras_require={
        "dev": [
            "mkdocs",
            "mkdocs-material",
            "pytest",
        ],
    },
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: SQL",
        "Programming Language :: Python :: 3 :: Only",
    ],
)
