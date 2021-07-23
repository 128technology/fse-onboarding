import setuptools

setuptools.setup(
    name="fse",
    version="1.0.0",
    description="FSE Provisioner library modules",
    packages=setuptools.find_packages(),
    install_requires=["provisioner", "requests", "urllib3"],
    python_requires=">=3.6",
)
