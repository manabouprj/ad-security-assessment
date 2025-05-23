from setuptools import setup, find_packages

setup(
    name="ad-security-assessment",
    version="1.0.0",
    packages=find_packages(include=['src', 'src.*']),
    package_dir={'': '.'},
    include_package_data=True,
    install_requires=[
        line.strip()
        for line in open("requirements.txt")
        if line.strip() and not line.startswith("#")
    ],
    python_requires=">=3.8",
) 