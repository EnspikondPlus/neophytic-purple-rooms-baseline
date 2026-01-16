# Neophytic Rooms Purple Agent Baseline

A purple agent creeated for the AgentBeats competition using the template for building [A2A (Agent-to-Agent)](https://a2a-protocol.org/latest/) agents.

## Project Structure

```
src/
├─ server.py      # Server setup and agent card configuration
├─ executor.py    # A2A request handling
├─ agent.py       # Agent implementation
└─ messenger.py   # A2A messaging utilities
tests/
├─ utils.py       # Helper for agent tests
└─ test_agent.py  # Agent tests
Dockerfile        # Docker configuration
pyproject.toml    # Python dependencies
.github/
└─ workflows/
   └─ test-and-publish.yml # CI workflow
```

## Getting Started

To see how to make a purple agent for AgentBeats, see this [draft PR](https://github.com/RDI-Foundation/agent-template/pull/8).

## Running Server Locally
```bash
uv sync

uv run purple-server
```

```bash
docker build -t purple-agent .

# Preconfigured run (run this first, before starting green agent)
docker run --rm --name purple-container --network agent-net -p 8000:8000 purple-agent --host 0.0.0.0 --port 8000 --card-url http://purple-container:8000
```

## About the Baseline
This the baseline model for the Neophytic Rooms Green Agent and associated benchmark. It attempts to solve the rooms puzzles in a mostly random way and does not perform well. The goal was to test environment and docker connection functionality, rather than create a necessarily powerful algorithm.