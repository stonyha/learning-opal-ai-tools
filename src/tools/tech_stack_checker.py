import logging
import os
from pathlib import Path
from pydantic import BaseModel
from opal_tools_sdk import tool
from fastapi import HTTPException

# Vercel requires writing files only to /tmp directory
# Set XDG_DATA_HOME environment variable before importing webtech
os.environ['XDG_DATA_HOME'] = '/tmp'

# Create webtech data directory in /tmp
webtech_data_dir = Path("/tmp/.local/share/webtech")
webtech_data_dir.mkdir(parents=True, exist_ok=True)

# Also create /tmp/webtech as alternative
Path("/tmp/webtech").mkdir(parents=True, exist_ok=True)

# Monkey patch both Path.home() and os.mkdir to force webtech to use /tmp
_original_home = Path.home
_original_mkdir = os.mkdir

@classmethod
def _patched_home(cls):
    """Return /tmp as home directory for webtech"""
    return Path("/tmp")

def _patched_mkdir(path, mode=0o777, *, dir_fd=None):
    """Patched mkdir that redirects webtech paths to /tmp and creates parent directories"""
    path_str = str(path)
    # Redirect any webtech-related paths to /tmp
    if 'webtech' in path_str:
        # Always use /tmp/.local/share/webtech for webtech directories
        new_path = Path("/tmp/.local/share/webtech")
        new_path.mkdir(parents=True, exist_ok=True, mode=mode)
        return
    # For other paths, try to create with parents
    try:
        Path(path).mkdir(parents=True, exist_ok=True, mode=mode)
    except (OSError, PermissionError):
        _original_mkdir(path, mode, dir_fd=dir_fd)

# Apply patches before importing webtech
Path.home = _patched_home
os.mkdir = _patched_mkdir

try:
    import webtech
    # Restore original functions after import
    Path.home = _original_home
    os.mkdir = _original_mkdir
    
    # Ensure DATA_DIR is set correctly
    try:
        from webtech import database
        if hasattr(database, 'DATA_DIR'):
            database.DATA_DIR = str(webtech_data_dir)
    except (ImportError, AttributeError):
        pass
except Exception:
    # Restore original functions even if import fails
    Path.home = _original_home
    os.mkdir = _original_mkdir
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