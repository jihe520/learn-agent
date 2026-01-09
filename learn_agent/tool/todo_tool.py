from learn_agent.tool.toolkit import Toolkit
from pydantic import BaseModel


class Todo(BaseModel):
    content: str
    status: str
    activeForm: str


class TodoTool(Toolkit):
    def __init__(self, **kwargs):
        super().__init__(
            name="Todo",
            tools=[self.update_todos],
            **kwargs,
        )
        self.todos = []

    def update_todos(self, items: list[Todo]) -> str:
        """
        Validate and update the todo list.

        The model sends a complete new list each time. We validate it,
        store it, and return a rendered view that the model will see.

        Validation Rules:
        - Each item must have: content, status, activeForm
        - Status must be: pending | in_progress | completed
        - Only ONE item can be in_progress at a time
        - Maximum 20 items allowed

        Args:
            items (list[Todo]): New todo items
             - content (str): Task description
             - status (str): One of "pending", "in_progress", "completed"
             - activeForm (str): Current action being performed (if any)
        Returns:
            Rendered text view of the todo list
        """
        validated = []
        in_progress_count = 0
        for i, item in enumerate(items):
            # Extract and validate fields
            content = str(item.content).strip()
            status = str(item.status).lower()
            active_form = str(item.activeForm).strip()

            # Validation checks
            if not content:
                raise ValueError(f"Item {i}: content required")
            if status not in ("pending", "in_progress", "completed"):
                raise ValueError(f"Item {i}: invalid status '{status}'")
            if not active_form:
                raise ValueError(f"Item {i}: activeForm required")

            if status == "in_progress":
                in_progress_count += 1

            validated.append(
                {"content": content, "status": status, "activeForm": active_form}
            )

        # Enforce constraints
        if len(validated) > 20:
            raise ValueError("Max 20 todos allowed")
        if in_progress_count > 1:
            raise ValueError("Only one task can be in_progress at a time")
        self.todos = validated

        return self.render()

    def render(self) -> str:
        """
        Render the todo list as human-readable text.

        Format:
            [x] Completed task
            [>] In progress task <- Doing something...
            [ ] Pending task

            (2/3 completed)

        This rendered text is what the model sees as the tool result.
        It can then update the list based on its current state.
        """
        if not self.todos:
            return "No todos."

        lines = []
        for item in self.todos:
            if item["status"] == "completed":
                lines.append(f"[x] {item['content']}")
            elif item["status"] == "in_progress":
                lines.append(f"[>] {item['content']} <- {item['activeForm']}")
            else:
                lines.append(f"[ ] {item['content']}")

        completed = sum(1 for t in self.todos if t["status"] == "completed")
        lines.append(f"\n({completed}/{len(self.todos)} completed)")

        return "\n".join(lines)
