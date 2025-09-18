from setuptools import setup, find_packages

setup(
    name="tradingapi",
    version="0.1.0",
    author="Nerve Solutions",
    description="A Python SDK for Connecting to Mirae API and Streaming API",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="",
    packages=find_packages(),
    install_requires=[
        "autobahn", 
        "requests",
        "responses",
        "pytest",
        "setuptools",
        "twisted"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
)