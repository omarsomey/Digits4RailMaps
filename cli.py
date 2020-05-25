setup(
    name="recording tool",
    version="1.0.0",
    description="Recording video and GPS stream",
    long_description=README,
    url="https://github.com/omarsomey/Digits4RailMaps",
    author="Omar Somai",
    author_email="omar.somai@knorr-bremse.com",
    license="KB",
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    packages=["rectool"],
    include_package_data=True,
    install_requires=[
        "feedparser", "html2text", "importlib_resources", "typing"
    ],
    entry_points={"console_scripts": ["realpython=reader.__main__:main"]},
)