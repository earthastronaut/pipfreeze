import re
from setuptools import setup

short_description = "Tool to produce better formatted pip freeze."
with open('README.md') as f:
    long_description = f.read()


with open('pipfreeze.py') as f:
    version = next(
        re.finditer(
            r'\n__version__ *= *[\'\"]([0-9\.]+)[\'\"]',
            f.read(),
        )
    ).groups()[0]


setup(
    name='pipfreeze',
    version=version,
    author='Dylan Gregersen',
    author_email='an.email0101@gmail.com',
    url='https://github.com/earthastronaut/pipfreeze',
    license='MIT',
    description=short_description,
    long_description=long_description,
    long_description_content_type='text/markdown',
    py_modules=['pipfreeze'],
    entry_points={
        'console_scripts': ['pipfreeze = pipfreeze:cli']
    },
    python_requires='>=2.7',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ]
)
