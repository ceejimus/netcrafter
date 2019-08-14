import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="netcrafter",
    version="0.0.1",
    author="ceejimus",
    author_email="cj@atmoscape.net",
    description="Scrapes NetCraft site reports to file",
    # long_description=long_description,
    # long_description_content_type="text/markdown",
    url="https://github.com/cj-atmoscape/netcrafter",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    scripts=[
        'bin/netcrafter'
    ],
)