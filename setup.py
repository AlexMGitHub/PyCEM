from setuptools import setup, find_packages

setup(
    name="pycem",
    packages=find_packages(where="src"),
    package_dir={'': 'src'}
)
