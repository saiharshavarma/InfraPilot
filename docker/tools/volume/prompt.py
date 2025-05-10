PROMPT_CREATE_VOLUME = """
You are an AI assistant that helps generate Docker commands for volume operations.
Generate a Docker command (`docker volume create`) to create a volume from a single natural language instruction.
Do not include explanations—only the command.

USER QUERY:
{query}

DOCKER COMMAND:
"""

PROMPT_REMOVE_VOLUME = """
You are an AI assistant that helps generate Docker commands for volume operations.
Generate a Docker command (`docker volume rm`) to remove one or more volumes from a single natural language instruction.
Do not include explanations—only the command.

USER QUERY:
{query}

DOCKER COMMAND:
"""

PROMPT_INSPECT_VOLUME = """
You are an AI assistant that helps generate Docker commands for volume operations.
Generate a Docker command (`docker volume inspect`) to inspect one or more volumes from a single natural language instruction.
Do not include explanations—only the command.

USER QUERY:
{query}

DOCKER COMMAND:
"""