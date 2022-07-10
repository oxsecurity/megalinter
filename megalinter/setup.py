from setuptools import setup

setup(
    name="megalinter",
    version="0.1",
    description="MegaLinter",
    url="http://github.com/oxsecurity/megalinter",
    author="Nicolas Vuillamy",
    author_email="nicolas.vuillamy@gmail.com",
    license="MIT",
    packages=["megalinter", "megalinter.linters", "megalinter.reporters"],
    install_requires=[
        "gitpython",
        "jsonpickle",
        "multiprocessing_logging",
        "pychalk",
        "pygithub",
        "python-gitlab",
        "commentjson",
        "pytablewriter",
        "pyyaml",
        "requests",
        "terminaltables",
        "importlib-metadata>=3.10"
        # "flask-restful"
    ],
    zip_safe=False,
)
