import logging
from pydantic import BaseModel
import webtech
from opal_tools_sdk import tool
from fastapi import HTTPException

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