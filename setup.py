from setuptools import setup, find_packages

setup(
    name="termnotes",  # This is your package name
    version="19.3",
    packages=find_packages(),
    install_requires=[
        "appdirs",
        "gnureadline",
        "pyperclip",
        "rich",
        "termcolor",  # Keep this if you actually use it in your code elsewhere
    ],
    entry_points={
        'console_scripts': [
            'termnotes=termnotes.main:run',  # 'termnotes' will call the `run` function from termnotes.main
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
