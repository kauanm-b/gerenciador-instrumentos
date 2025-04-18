from setuptools import setup, find_packages

setup(
    name="instrumentos",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "sqlalchemy==2.0.27",
        "requests==2.31.0",
        "pandas==2.2.0",
        "numpy==1.26.4",
        "beautifulsoup4==4.12.3",
        "python-dotenv==1.0.1",
        "openpyxl==3.1.2",
        "PyQt6==6.6.1",
        "PyQt6-Qt6==6.6.1",
        "PyQt6-sip==13.6.0",
        "python-dateutil==2.8.2",
        "pytz==2024.1",
        "lxml==5.1.0"
    ],
    python_requires=">=3.8",
    author="Kauã Barcellos",
    description="Sistema de Gerenciamento de Instrumentos",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
) 