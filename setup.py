from setuptools import setup, find_packages

setup(
    name="termnotes",  # This is your package name
    version="16.5",
    packages=find_packages(),
    install_requires=[
        "termcolor",  # Add any dependencies you need here
    ],
    entry_points={
        'console_scripts': [
            'termnotes=termnotes.main:run',  # 'tnotes' will call the `run` function from tnotes.main
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
