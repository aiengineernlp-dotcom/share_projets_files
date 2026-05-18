from setuptools import setup, find_packages

setup(
    name="medical_data_collection",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "aiohttp",
        "asyncio",
        "beautifulsoup4",
        "python-dotenv",
        "requests",
        "selenium",
        "pymongo",
        "praw",
        "instaloader",
        "linkedin-api",
        "pandas",
        "numpy",
        "nltk",
        "scikit-learn",
        "pydantic",
        "TikTokApi"
    ]
) 