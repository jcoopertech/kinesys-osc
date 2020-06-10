import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

" THIS SCRIPT IS NOT FOR PRODUCTION AND IS A SAMPLE ONLY "

"""

        DO NOT RUN THIS CODE

"""


#setuptools.setup(
    name="example-pkg-YOUR-USERNAME-HERE", # Replace with your own username
    version="0.0.0",
    author="James Cooper",
    author_email="james@jcooper.tech",
    description="A small example package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
