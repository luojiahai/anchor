import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="anchor",
    version="0.0.1",
    author="luojiahai",
    author_email="luo@jiahai.co",
    description="Anchor Programming Language",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/luojiahai/anchor",
    project_urls={
        "Bug Tracker": "https://github.com/luojiahai/anchor/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "."},
    packages=setuptools.find_packages(where="."),
    python_requires=">=3.9",
    entry_points = {
        'console_scripts': ['an=anchor.__main__:main'],
    }
)
