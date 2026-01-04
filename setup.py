from setuptools import setup, find_packages

# Read requirements from requirements.txt
with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="algorithmic_trading_utilities",
    version="0.1.2",
    packages=find_packages(),
    install_requires=requirements,  # <- automatically installs all dependencies
    description="Reusable utilities for algorithmic trading pipelines.",
    python_requires=">=3.8",
)
