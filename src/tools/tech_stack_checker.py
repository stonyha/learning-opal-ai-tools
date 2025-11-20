import logging
import os
from pathlib import Path
from pydantic import BaseModel
from opal_tools_sdk import tool
from fastapi import HTTPException

# Vercel requires writing files only to /tmp directory
# Monkey patch Path.home() to return /tmp during webtech import
# This ensures webtech uses /tmp instead of the home directory
_original_home = Path.home
webtech_data_dir = Path("/tmp/.local/share/webtech")
webtech_data_dir.mkdir(parents=True, exist_ok=True)

def _patched_home_func(cls):
    """Temporarily return /tmp as home for webtech initialization"""
    return Path("/tmp")

# Patch Path.home() before importing webtech
Path.home = classmethod(_patched_home_func)

try:
    import webtech
    # After import, restore original Path.home()
    Path.home = _original_home
    
    # Also patch DATA_DIR directly to ensure it uses /tmp
    try:
        from webtech import database
        database.DATA_DIR = str(webtech_data_dir)
    except (ImportError, AttributeError):
        # Try alternative import path
        if hasattr(webtech, 'database'):
            webtech.database.DATA_DIR = str(webtech_data_dir)
except Exception:
    # Restore Path.home() even if import fails
    Path.home = _original_home
    raise

class CheckTechStackParams(BaseModel):
    url: str

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NitecoOpalToolsTest")

@tool(
  "tech_stack_discovery", 
  "Analyzes a website's technology stack. Use when user wants to identify technologies, frameworks, or tools used by a website.", 
)
async def tech_stack_discovery(params: CheckTechStackParams):
    url = params.url
    if not params or not url:
        raise HTTPException(status_code=400, detail="URL is required")
    logger.info(f"Received tech stack discovery request for URL: {url}")
    try:
        wt = webtech.WebTech(options={'json': True})
        technologies = wt.start_from_url(url)
        logger.info(f"Technologies discovered: {technologies}")
        
        # Extract technology names from the response
        tech_list = []
        if technologies and 'tech' in technologies:
            for tech in technologies['tech']:
                tech_name = tech.get('name')
                tech_version = tech.get('version')
                if tech_name:
                    tech_list.append({
                        "name": tech_name,
                        "version": tech_version if tech_version else ""
                    })
        
        return {
            "technologies": tech_list,
            "count": len(tech_list)
        }
    
    except Exception as e:
        logger.error(f"Error checking tech stack: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")