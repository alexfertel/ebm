from setuptools import setup

setup(
    name="ebmc",
    version="0.1",
    packages=[
        'ebmc',
        'ebmc.core'
    ],
    install_requires=['imbox>=0.9.6'],
    author="Alexander Gonzalez, Sandor Martin",
    author_email="alexfertel97@gmail.com, s.martin@estudiantes.matcom.uh.cu",
    description="This an implementation of a client of an Email Based Middleware",
    project_urls={
        "Documentation": "https://github.com/white41/ebm",
        "Source Code": "https://github.com/white41/ebm/README.md",
    }
)
