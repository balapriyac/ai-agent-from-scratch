"""
A minimal AI agent built from scratch against the Anthropic API, with no
agent framework involved.

Contains:
- A tool (get_order_status) with a schema the model can read
- An Agent class that runs the tool-calling loop
- Memory: self.messages persists across calls to Agent.run()

Companion code for "How and Why to Build an AI Agent From Scratch in Python."
"""

import anthropic

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment

MODEL = "claude-sonnet-4-5"


# ---------------------------------------------------------------------------
# Tool: order lookup
# ---------------------------------------------------------------------------

orders_db = {
    "4471": {"status": "shipped", "carrier": "UPS", "eta": "2 days"},
    "4472": {"status": "processing", "carrier": None, "eta": None},
}


def get_order_status(order_id: str) -> dict:
    return orders_db.get(order_id, {"error": "No order found with that ID"})


get_order_status_schema = {
    "name": "get_order_status",
    "description": (
        "Looks up the current status of a customer order by its ID. "
        "Use this any time a question depends on current order data "
        "rather than general policy information."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "order_id": {
                "type": "string",
                "description": "The order ID to look up, e.g. '4471'",
            },
        },
        "required": ["order_id"],
    },
}

TOOLS = [get_order_status_schema]
TOOL_MAP = {"get_order_status": get_order_status}


# ---------------------------------------------------------------------------
# Agent with memory
# ---------------------------------------------------------------------------

class Agent:
    def __init__(self, tools, tool_map, max_iterations: int = 6):
        self.tools = tools
        self.tool_map = tool_map
        self.max_iterations = max_iterations
        self.messages = []

    def run(self, user_input: str) -> str:
        self.messages.append({"role": "user", "content": user_input})

        for _ in range(self.max_iterations):
            response = client.messages.create(
                model=MODEL,
                max_tokens=512,
                tools=self.tools,
                messages=self.messages,
            )
            self.messages.append({"role": "assistant", "content": response.content})

            if response.stop_reason != "tool_use":
                return response.content[0].text

            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    function = self.tool_map[block.name]
                    output = function(**block.input)
                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": str(output),
                        }
                    )
            self.messages.append({"role": "user", "content": tool_results})

        return "Stopped after max iterations without a final answer."


if __name__ == "__main__":
    agent = Agent(tools=TOOLS, tool_map=TOOL_MAP)

    print(agent.run("What is the status of order #4471?"))
    print(agent.run("And when will it arrive?"))

