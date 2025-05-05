from setuptools import setup, find_packages

setup(
    name="mood-music-recommender",
    version="0.1",
    packages=find_packages(where="backend"),
    package_dir={"": "backend"},
    install_requires=[
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "python-dotenv>=0.19.0",
        "requests>=2.26.0",
        "numpy>=1.21.0",
        "scikit-learn>=1.0.0",
        "joblib>=1.0.0",
        "transformers>=4.12.0",
        "torch>=1.9.0",
        "pydantic>=1.8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "black>=21.0",
            "flake8>=3.9.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "mood-music=app.main:main",
        ],
    },
)