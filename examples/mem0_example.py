"""Example usage of Mem0Tool for memory management."""
import asyncio
from learn_agent.tool.mem0_tool import Mem0Tool


async def main():
    """Demonstrate Mem0Tool functionality."""
    # Initialize with a user ID
    memory_tool = Mem0Tool(user_id="demo_user")

    # List available tools
    print("Available tools:")
    for schema in memory_tool.list_tools_schemas():
        print(f"  - {schema['function']['name']}")

    print("\n=== Adding memories ===")
    # Add memories
    result = memory_tool.add_memory("My name is John and I prefer dark mode")
    print(result)

    result = memory_tool.add_memory("I am allergic to peanuts and shellfish")
    print(result)

    print("\n=== Searching memories ===")
    # Search memories
    result = memory_tool.search_memory("What are my food preferences?")
    print(result)

    print("\n=== Getting all memories ===")
    # Get all memories
    result = memory_tool.get_all_memories()
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
