import setuptools

setuptools.setup(
    name="provisioner",
    version="1.0.0",
    description="Provisioner library modules",
    packages=setuptools.find_packages(),
    install_requires=[
        "attrs",
        "click",
        "jinja2",
        "lxml",
        "pyyaml",
        "ncclient",
        "requests",
        "urllib3",
    ],
    python_requires=">=3.6",
)
