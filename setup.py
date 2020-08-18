import setuptools

with open('README.md', 'r') as f:
    long_description = f.read()

setuptools.setup(
    name='antibiotics',
    description='a treatment for PANDAS',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Derrick W. Turk',
    author_email='dwt@terminusdatascience.com',
    url='https://github.com/derrickturk/antibiotics',
    version='0.2',
    packages=setuptools.find_packages(),
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
    package_data={'antibiotics': ['py.typed']},
    zip_safe=False,
)
