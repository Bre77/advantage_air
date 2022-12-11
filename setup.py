import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="advantage_air",
    version="0.4.2",
    author="Brett Adams",
    author_email="brett@ba.id.au",
    description="API helper for Advantage Air's MyAir and e-zone API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Bre77/advantage_air",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=["aiohttp"],
)
