from setuptools import setup, find_packages

# Read requirements from requirements.txt
with open("requirements.txt") as f:
    requirements = f.read().splitlines()

with open("VERSION") as f:
    version = f.read().strip()

setup(
    name="algorithmic_trading_utilities",
    version=version,
    packages=find_packages(),
    install_requires=requirements,  # <- automatically installs all dependencies
    description="Reusable utilities for algorithmic trading pipelines.",
    python_requires=">=3.8",
)
