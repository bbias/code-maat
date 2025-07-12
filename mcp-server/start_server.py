#!/usr/bin/env python3
"""
Startup script for Code Maat MCP Server.
This script ensures proper error handling and logging.
"""

import sys
import os
import logging
import asyncio

# Add the source directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, "src")
sys.path.insert(0, current_dir)
sys.path.insert(0, src_dir)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(current_dir, "mcp_server.log")),
        logging.StreamHandler(sys.stderr)
    ]
)

logger = logging.getLogger(__name__)

async def main():
    """Main entry point for the MCP server."""
    try:
        logger.info("Starting Code Maat MCP Server...")
        
        # Import and start the server
        try:
            from src.mcp_server import CodeMaatMCPServer
        except ImportError:
            # Fallback for different import contexts
            from mcp_server import CodeMaatMCPServer
        
        server = CodeMaatMCPServer()
        await server.run()
        
    except ImportError as e:
        logger.error(f"Failed to import MCP server: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())