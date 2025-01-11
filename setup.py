from setuptools import setup, find_packages

setup(
    name="wordtoken",
    version="0.1.0",
    description="A unified library for interacting with LLMs, managing tokens, and estimating costs.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Zev Uhuru",
    author_email="zev@esy.com",
    url="https://wordtoken.com",
    packages=find_packages(),
    install_requires=[
        "openai>=0.27.0",
        "tiktoken>=0.4.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    license="Apache 2.0",  
)