#!/usr/bin/env python3
"""Verify that all imports work correctly."""

import sys

def test_imports():
    """Test importing all main modules."""
    modules_to_test = [
        ("src.agents.base", "BaseAgent"),
        ("src.agents.supervisor", "Supervisor"),
        ("src.agents.research_agent", "ResearchAgent"),
        ("src.core.config", "settings"),
        ("src.core.database.models", "Agent"),
        ("src.core.database.session", "SessionLocal"),
        ("src.core.messaging.queue", "MessageQueue"),
        ("src.web.dashboard.app", "app"),
    ]

    for module_name, attr_name in modules_to_test:
        try:
            __import__(module_name)
            print(f"✓ {module_name} imports successfully")
        except ImportError as e:
            print(f"✗ Failed to import {module_name}: {e}")
            return False

    print("\nAll imports successful!")
    return True

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)