# mcp_server/main.py
import uvicorn
from fastapi import Request
from fastapi.responses import PlainTextResponse
from mcp.server.fastmcp import FastMCP # Correct import
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
import os
from dotenv import load_dotenv

load_dotenv()

# Create a FastMCP server instance.
# Pass host and port directly to the FastMCP constructor for HTTP transport.
mcp_app = FastMCP(
    title="AI Onboarding Assistant MCP Server",
    description="Exposes tools for LLM to extract client information.",
    host="0.0.0.0",  # Bind to all available network interfaces
    port=8001        # Listen on port 8001
)

# Define Pydantic models for your tool inputs/outputs
class ClientInfo(BaseModel):
    client_name: Optional[str] = Field(None, description="The full name of the potential client.")
    company_name: Optional[str] = Field(None, description="The company name of the potential client.")
    contact_number: Optional[str] = Field(None, description="The primary contact phone number of the client.")
    email: Optional[str] = Field(None, description="The primary email address of the client.")
    service_interest: Optional[str] = Field(None, description="A brief description of the services the client is interested in, derived from the conversation.")

# Register your tool using the mcp_app.tool() decorator
@mcp_app.tool()
def extract_client_info_tool(transcript: str) -> ClientInfo:
    """
    Extracts key client information (name, company, contact number, email, service interest, deal size estimate)
    from a call transcript. This tool should be called when sufficient information is present in the transcript.
    """
    print(f"MCP Server: 'extract_client_info_tool' called with transcript segment (first 100 chars): {transcript[:100]}...")
    return ClientInfo() # Return an empty instance for schema definition

# Add a custom HTTP route using @mcp_app.custom_route
@mcp_app.custom_route("/", methods=["GET"])
async def read_root(request: Request) -> PlainTextResponse:
    """
    Health check endpoint for the MCP server.
    """
    return PlainTextResponse("AI Onboarding Assistant MCP Server is running!")

if __name__ == "__main__":
    print(f"Attempting to run FastMCP using mcp_app.run() on http://0.0.0.0:8001...")
    mcp_app.run(transport="streamable-http") # Specify the transport here