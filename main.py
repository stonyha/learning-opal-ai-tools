from fastapi import FastAPI
from opal_tools_sdk import ToolsService


app = FastAPI()
opal_tools_service = ToolsService(app)

# Import your tool here
from src.tools.url_slug_generator import generate_url_slug
from src.tools.broken_link_checker import broken_link_checker