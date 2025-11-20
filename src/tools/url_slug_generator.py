import re
from pydantic import BaseModel, Field
from opal_tools_sdk import tool
from unidecode import unidecode
from fastapi import HTTPException

class UrlSlugGenerator(BaseModel):
    title: str = Field(description="The title to convert into a URL slug")

@tool(
    name="url_slug_generator", 
    description="Convert a title into a short, clean and SEO-friendly URL slug by removing special characters and stop words. \
        The slug must be at least 5 characters long. If the slug is less than 5 characters long, raise a 400 Bad Request Error. \
        Also return the length of the original title and the length of the slug for making the comparison.",
)
async def generate_url_slug(params: UrlSlugGenerator):
    # Step 1: Convert to lowercase
    slug = params.title.lower()
    
    # Step 2: Remove Vietnamese diacritics (unidecode)
    slug = unidecode(slug)
    
    # Step 3: Remove common stop words
    stop_words = ['the', 'a', 'of', 'and', 'in', 'to', 'for', 'on', 'at', 'by']
    words = slug.split()
    slug = ' '.join([word for word in words if word not in stop_words])
    
    # Step 4: Replace spaces and unnecessary characters with hyphen
    slug = re.sub(r'[,:\s]+', '-', slug)
    
    # Step 5: Remove all non-alphanumeric characters except hyphens
    slug = re.sub(r'[^a-z0-9-]', '', slug)
    
    # Step 6: Strip leading/trailing hyphens and reduce multiple hyphens to single hyphen
    slug = re.sub(r'-+', '-', slug).strip('-')
    
    # Step 7: Validate minimum length
    if len(slug) < 5:
        raise HTTPException(status_code=400, detail="The resulting slug is critically short and requires a more detailed source title")
    
    return {
        "slug": slug,
        "original_title": params.title,
        "original_length": len(params.title),
        "slug_length": len(slug)
    }
