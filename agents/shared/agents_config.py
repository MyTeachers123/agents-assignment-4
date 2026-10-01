"""
Configuration for Google ADK-based Agents (GIVEN - fully implemented)
"""

import os
import logging

# Gemini Model Configuration
# Load from environment variable, default to gemini-3.8-flash
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

# Log which model is being used
logger = logging.getLogger(__name__)
logger.info(f"Using Gemini Model: {GEMINI_MODEL}")

# Google Cloud Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "")
GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

# Use Vertex AI or Gemini API
USE_VERTEX_AI = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "FALSE").upper() == "TRUE"

# MCP Server Configuration
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8080")

# Agent Server Ports
CUSTOMER_DATA_AGENT_PORT = 10020
SUPPORT_AGENT_PORT = 10021
HOST_AGENT_PORT = 10022

# Agent Server URLs
CUSTOMER_DATA_AGENT_URL = f"http://localhost:{CUSTOMER_DATA_AGENT_PORT}"
SUPPORT_AGENT_URL = f"http://localhost:{SUPPORT_AGENT_PORT}"
HOST_AGENT_URL = f"http://localhost:{HOST_AGENT_PORT}"
