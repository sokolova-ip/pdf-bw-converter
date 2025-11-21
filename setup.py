from setuptools import setup, find_packages

setup(
    name="pdf_bw_converter",
    version="1.0.0",
    description="Конвертер PDF в черно-белый с графическим интерфейсом",
    packages=find_packages(),
    install_requires=[
        "PyMuPDF==1.23.8",
        "Pillow==10.0.1",
    ],
    python_requires=">=3.7",
    author="Sokolova_IP",
    author_email="Sokolova_IP@example.com",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)