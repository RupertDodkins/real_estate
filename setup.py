from setuptools import setup, find_packages

setup(
    name="real_estate",
    version="0.1",
    author="Rupert Dodkins",
    author_email="rupertdodkins@gmail.com",
    description="A short description of your package",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/RupertDodkins/real_estate/",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        # Add your package's dependencies here
        'plotly',
        'kaleido',
    ],
)
