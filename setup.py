from setuptools import setup, find_packages


README = open('README.rst').read()


setup(
    name='djapi',
    version='0.3',
    author='Alexander Schepanovski',
    author_email='suor.web@gmail.com',

    description='The library of simple helpers to build API with Django.',
    long_description=README,
    url='https://github.com/Suor/djapi',
    license='BSD',

    packages=find_packages(),
    install_requires=[
        'django>=3.2',
        'funcy>=1.8,<3.0',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.23',
        'Framework :: Django',
        'Framework :: Django :: 3.2',
        'Framework :: Django :: 4.2',
        'Framework :: Django :: 5.0',

        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
