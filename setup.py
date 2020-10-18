from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='notetaking',
    version='0.1.5',
    description='Markdown -> HTML -> pdf on the fly',
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
        'Topic :: Text Processing :: Markup',
    ],
    keywords='markdown html pdf weasyprint',
    url='',
    author='Calum Baird',
    author_email='calum.baird7011@gmail.com',
    license='GPLv3',
    packages=find_packages(),
    install_requires=[
        'markdown', 'weasyprint', 'inotify', 'pygments', 'cairocffi'
    ],
    package_data={
      'notetaking': ['css/default.css', 'fonts/*'],
    },
    entry_points = {
        'console_scripts': ['notetaking=notetaking:main'],
    },
    include_package_data=True,
    zip_safe=False,
    python_requires='>=3.6'
)

print("\nMake sure you install mupdf as well!\n")
