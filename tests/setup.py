import os
import setuptools


#  INFO: install dev & extra dependencies
os.chdir(os.path.join(os.path.dirname(__file__), ".."))
scraby_dist = setuptools.distutils.core.run_setup("setup.py", stop_after="init")
requirements = scraby_dist.install_requires + scraby_dist.extras_require["dev"]
os.chdir(os.path.dirname(__file__))

setuptools.setup(
    name="scraby-tests",
    description="Tests for Scraby",
    url="https://github.com/dsp-shp/scraby",
    author="Ivan Derkach",
    author_email="dsp_shp@icloud.com",
    license="Apache License 2.0",
    package_dir={"scraby_tests": ""},
    install_requires=requirements,
)
