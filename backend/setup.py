from setuptools import setup, find_packages

setup(
    name="recipe-sharing",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "fastapi==0.104.1",
        "uvicorn==0.24.0",
        "sqlalchemy==2.0.23",
        "pydantic==2.10.1",
        "pydantic-settings==2.1.0",
        "python-jose==3.3.0",
        "passlib==1.7.4",
        "python-multipart==0.0.6",
        "redis==5.0.1",
        "psycopg2-binary==2.9.9",
        "python-dotenv==1.0.0",
        "authlib==1.2.1",
        "httpx==0.25.2",
        "supabase>=2.0.0",
        "uuid==1.30",
        "pytest==7.4.3",
        "pytest-asyncio==0.21.1"
    ],
) 