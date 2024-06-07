from setuptools import find_packages, setup

setup(
    name="fsmlib",
    version="0.0.1",
    description="A framework for building state machines",
    url="https://github.com/ne3x7/fsmlib",
    author="Nikolai Stulov",
    packages=find_packages(),
    author_email="nickstulov@gmail.com",
    install_requires=open("requirements.txt").read(),
    include_package_data=True,
)
