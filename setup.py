from setuptools import setup, find_packages


README = open('README.rst').read()


setup(
    name='djapi',
    version='0.2',
    author='Alexander Schepanovski',
    author_email='suor.web@gmail.com',

    description='The library of simple helpers to build API with Django.',
    long_description=README,
    url='https://github.com/Suor/djapi',
    license='BSD',

    packages=find_packages(),
    install_requires=[
        'django>=2.1',
        'funcy>=1.8,<2.0',
        'six>=1.10.0',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Framework :: Django',
        'Framework :: Django :: 2.1',
        'Framework :: Django :: 2.2',
        'Framework :: Django :: 3.0',

        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
