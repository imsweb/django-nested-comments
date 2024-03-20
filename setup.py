from setuptools import setup, find_packages
import comments

setup(
    name='django-nested-comments',
    version=comments.__version__,
    description='A Django application for handling comment uploads and associating them to arbitrary models.',
    author='Noah Lefcourt',
    author_email='lefcourn@imsweb.com',
    url='https://github.com/imsweb/django-nested-comments',
    license='BSD',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'django-mptt~=0.14.0',
        'nh3',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Utilities',
    ]
)
