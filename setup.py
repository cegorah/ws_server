import os
from typing import List
from importlib.machinery import SourceFileLoader

from pkg_resources import parse_requirements
from setuptools import setup, find_packages

source_path = "src"
module_name = "WebSocketServer"
module = SourceFileLoader(
    module_name, os.path.join(source_path, module_name, "__init__.py")
).load_module()


def load_req(fname: str) -> List:
    req_list = list()
    with open(fname, "r") as req_file:
        for req in parse_requirements(req_file.read()):
            extra = '[{}]'.format(','.join(req.extras)) if req.extras else ""
            req_list.append("{}{}{}".format(req.name, extra, req.specifier))
    return req_list


setup(
    name=module_name,
    version=module.__version__,
    author=module.__author__,
    license=module.__license__,
    description=module.__doc__,
    long_description=open('README.md').read(),
    url='https://github.com/cegorah/task_manager',
    python_requires='>=3.8',
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=load_req("requirements.txt"),
    extras_require={'dev': load_req('requirements.dev.txt')},
    include_package_data=True,
    entry_points={'console_scripts':
                      '{0} = {0}.server:main'.format(module_name),
                  }
)
