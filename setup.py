import os

from setuptools import (
    find_packages,
    setup,
)


def gen_data_files(*dirs):
    results = []

    for src_dir in dirs:
        for root, dirs, files in os.walk(src_dir):
            results.append((root, map(lambda f: root + "/" + f, files)))
    return results


def parse_requirements(filename):
    """ load requirements from a pip requirements file """
    lineiter = (line.strip() for line in open(filename))
    return [line for line in lineiter if line and not line.startswith("#")]


setup(
    name='cxyx_monitor',
    version="0.0.1",
    description='A mini monitor framework, for cxyx',
    packages=find_packages(exclude=[]),
    include_package_data=True,

    author='chenxiyuxiao',
    author_email='18883325829@163.com',
    license='BSD 2-Clause License',
    package_data={'': ['*.*', "*"],
                  "front": ["static/*/*", "templates/*.html"]
                  },
    url='https://github.com/Thixiaoxiao/cxyx_monitor',
    install_requires=parse_requirements("requirements.txt"),
    zip_safe=False,
    classifiers=[
        'Programming Language :: Python',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: Unix',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    entry_points={
        'console_scripts': [
            'monitor = cxyx_monitor.__main__:monitor'
        ]
    },
)
