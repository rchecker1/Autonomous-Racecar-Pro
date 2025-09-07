from setuptools import setup, find_packages

setup(
    name='autonomous-racecar',
    version='1.0.0',
    description='Professional Autonomous Racing Car System',
    author='Your Name',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'torch',
        'torchvision', 
        'opencv-python',
        'numpy',
        'matplotlib',
        'pyyaml',
        'ipywidgets',
        'jupyterlab'
    ],
    python_requires='>=3.8',
)
