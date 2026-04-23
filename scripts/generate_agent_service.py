#!/usr/bin/env python3
"""
Generate Docker Compose service entries for all registered Aetherion agents.
Each agent becomes a separate microservice using the generic agent server.
"""

from agents.colleges.all_colleges import AGENT_REGISTRY

print("# Auto-generated agent microservices")
print("# Run: python scripts/generate_agent_services.py >> docker-compose.yml")
print()

for agent_name in sorted(AGENT_REGISTRY.keys()):
    service_name = agent_name.lower()
    print(f"  {service_name}:")
    print(f"    build:")
    print(f"      context: .")
    print(f"      dockerfile: agents/services/Dockerfile.agent")
    print(f"    container_name: aetherion-{service_name}")
    print(f"    environment:")
    print(f"      - AETHERION_AGENT={agent_name}")
    print(f"      - OLLAMA_HOST=ollama:11434")
    print(f"    restart: unless-stopped")
    print()
