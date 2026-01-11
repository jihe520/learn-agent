"""Mem0Tool - Memory management using mem0 for persistent storage."""
from typing import Any
from mem0 import MemoryClient
from learn_agent.tool.toolkit import Toolkit


class Mem0Tool(Toolkit):
    """Memory tool using mem0 for persistent storage.

    Provides methods to add, search, retrieve, and delete memories.
    """

    def __init__(self, user_id: str = "default", **kwargs):
        """Initialize Mem0Tool.

        Args:
            user_id (str): The user ID for memory storage. Defaults to "default".
        """
        self.user_id = user_id
        self.client = MemoryClient()
        super().__init__(
            name="Mem0Tool",
            tools=[self.add_memory, self.search_memory, self.get_all_memories, self.delete_memory],
            **kwargs,
        )

    def add_memory(self, content: str) -> str:
        """Add a new memory.

        Args:
            content (str): The memory content to store.

        Returns:
            str: Confirmation message with memory ID.
        """
        result = self.client.add([{"role": "user", "content": content}], user_id=self.user_id)
        return f"Memory added: {result}"

    def search_memory(self, query: str) -> str:
        """Search for relevant memories.

        Args:
            query (str): The search query.

        Returns:
            str: Search results as string.
        """
        results = self.client.search(query, user_id=self.user_id, filters={"user_id": self.user_id})
        return str(results)

    def get_all_memories(self) -> str:
        """Get all stored memories for the user.

        Returns:
            str: All memories as string.
        """
        results = self.client.get_all(user_id=self.user_id, filters={"user_id": self.user_id})
        return str(results)

    def delete_memory(self, memory_id: str) -> str:
        """Delete a specific memory.

        Args:
            memory_id (str): The ID of the memory to delete.

        Returns:
            str: Confirmation message.
        """
        self.client.delete(memory_id, user_id=self.user_id)
        return f"Memory {memory_id} deleted"
