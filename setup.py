from setuptools import setup, find_packages

setup(
    name="pst",
    version="0.1.0",
    packages=find_packages(include=["pst", "pst.*"]),
    install_requires=[
        "pyyaml",
        "boto3>=1.26.0",
        "python-dotenv",
    ],
    entry_points={
        "console_scripts": [
            "pginit=pst.tools.pg_init:main",
            "pg=pst.tools.pg:main",
        ],
    },
    author="JakeDavisAtFanatics",
    author_email="jake.davis@betfanatics.com",
    description="PST (Platform Storage Tools) is a collection of tools for PostgreSQL database management and environment configuration",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/JakeDavisAtFanatics/platform-storage-tools",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
