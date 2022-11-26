import setuptools


with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="algofi-py-sdk",
    description="The official Algofi V1 Python SDK",
    author="Algofi, Inc.",
    author_email="founders@algofi.org",
    version="1.2.1",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    project_urls={
        "Source": "https://github.com/Algofiorg/algofi-py-sdk",
    },
    packages=setuptools.find_packages(),
    python_requires=">=3.8",
    package_data={"algofi.v1": ["contracts.json"]},
    include_package_data=True,
)
