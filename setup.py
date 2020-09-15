import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="advantageair",  # Replace with your own username
    version="0.0.1",
    author="Brett Adams",
    author_email="brett@ba.id.au",
    description="API helper for Advantage Airs MyAir and e-zone API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Bre77/advantageair",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
