from setuptools import setup, find_packages
import comments

setup(
    name='comments',
    version=comments.__version__,
    description='A Django application for handling comment uploads and associating them to arbitrary models.',
    author='Noah Lefcourt',
    author_email='lefcourn@imsweb.com',
    url='http://imsweb.com',
    license='BSD',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'mptt',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities',
    ]
)
