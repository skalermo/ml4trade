from setuptools import setup, find_packages

setup(
    name='ml4trade',
    version='0.2.0',
    url='https://github.com/skalermo/ml4trade',
    author='skalermo',
    author_email='skalermo@gmail.com',
    description='Machine learning for trading',
    packages=find_packages(),
    install_requires=[
        'gymnasium',
        'pandas >= 1.3.5',
        'matplotlib >= 3.5.3',
    ],
)
