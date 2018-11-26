import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="rwsch",
    version="0.1",
    author="Alexandr A.",
    author_email="flo0.webmaster@gmail.com",
    description="Package for scheduling publications based on historical data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/flo0web/rwsch",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
