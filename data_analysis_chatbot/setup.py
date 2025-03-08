from setuptools import setup, find_packages

setup(
    name="data_analysis_chatbot",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        line.strip() for line in open("requirements.txt", "r", encoding="utf-8").readlines()
    ],
    author="Sidhhanath tiwari",
    author_email="siddhanathtiwari7709@gmail.com",
    description="A RAG-based data analysis chatbot",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/data-analysis-chatbot",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "data-analysis-chatbot=data_analysis_chatbot.main:main",
        ],
    },
)