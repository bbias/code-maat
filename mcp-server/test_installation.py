#!/usr/bin/env python3
"""
Test script to verify Code Maat MCP Server installation.
"""

import sys
import os
import asyncio

# Add the source directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, "src")
sys.path.insert(0, src_dir)

async def test_installation():
    """Test the installation."""
    try:
        print("🧪 Testing Code Maat MCP Server Installation...")
        
        # Test 1: Import the server
        print("1. Testing server import...")
        from src.mcp_server import CodeMaatMCPServer
        server = CodeMaatMCPServer()
        print("   ✅ Server import successful")
        
        # Test 2: Check Code Maat JAR
        print("2. Testing Code Maat JAR...")
        jar_path = server.analysis_tools.wrapper.config.jar_path
        if os.path.exists(jar_path):
            print(f"   ✅ Code Maat JAR found: {jar_path}")
        else:
            print(f"   ❌ Code Maat JAR not found: {jar_path}")
            return False
        
        # Test 3: Test utility tools
        print("3. Testing utility tools...")
        result = await server.utility_tools.check_code_maat_status({})
        if "✅" in result[0].text:
            print("   ✅ Code Maat status check passed")
        else:
            print("   ❌ Code Maat status check failed")
            return False
        
        # Test 4: Test analysis tools
        print("4. Testing analysis tools...")
        tools = server.analysis_tools.get_tools()
        if len(tools) >= 7:
            print(f"   ✅ Found {len(tools)} analysis tools")
        else:
            print(f"   ❌ Expected at least 7 tools, found {len(tools)}")
            return False
        
        print("\n🎉 All tests passed! Code Maat MCP Server is ready to use.")
        print("\n📋 Next steps:")
        print("1. Restart Claude Desktop application")
        print("2. Look for 'code-maat' in the MCP servers list")
        print("3. Try commands like:")
        print("   - check_code_maat_status()")
        print("   - list_available_analyses()")
        print("   - generate_git_log() for your repositories")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_installation())
    sys.exit(0 if success else 1)