"""Quick test to verify MCP server imports and basic functionality"""
import asyncio
import sys
sys.path.insert(0, r'd:\Projects\Experiments\Colombo-Stock-Exchange-CSE-API-Documentation\mcp_server')

async def test_server():
    """Test that the server loads and can list tools"""
    try:
        from main import app, list_tools
        
        print("✓ MCP server imports successfully")
        print(f"✓ Server name: {app.name}")
        
        # List available tools
        tools = await list_tools()
        print(f"\n✓ Server exposes {len(tools)} tools:\n")
        
        for i, tool in enumerate(tools, 1):
            print(f"{i:2d}. {tool.name}")
            print(f"    {tool.description[:80]}...")
            if tool.inputSchema.get('required'):
                print(f"    Required params: {', '.join(tool.inputSchema['required'])}")
            print()
        
        print("✓ All tools loaded successfully!")
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_server())
    sys.exit(0 if success else 1)
