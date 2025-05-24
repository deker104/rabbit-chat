from setuptools import setup, find_packages

setup(
    name="rabbit-chat",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.12",
    install_requires=[
        "pika>=1.3.2",
        "prompt-toolkit>=3.0.51",
    ],
    extras_require={
        "dev": [
            "pytest>=8.3.5",
            "pytest-asyncio>=0.26.0",
            "pytest-mock>=3.14.0",
            "flake8>=7.1.1",
            "black>=25.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "rchat=rabbit_chat.console:main",
        ],
    },
    author="Daniil Shindov, Ivan Kalinin",
    author_email="dshindov@proton.me",
    description="A console-based chat application using RabbitMQ",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    keywords="chat, rabbitmq, console, messaging",
    url="https://github.com/deker104/rabbit-chat",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
    ],
)
