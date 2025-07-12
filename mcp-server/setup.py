from setuptools import setup, find_packages

setup(
    name="code-maat-mcp-server",
    version="0.1.0",
    description="Model Context Protocol server for Code Maat VCS analysis tool",
    author="Code Maat MCP Team",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "mcp>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=8.0.0",
            "pytest-asyncio>=0.21.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "code-maat-mcp-server=mcp_server:main",
        ],
    },
)