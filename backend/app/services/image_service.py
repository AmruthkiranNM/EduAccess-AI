import requests
import logging
import re

logger = logging.getLogger(__name__)

def fetch_educational_images(topic, limit=4):
    """
    Fetches curated educational images from Wikimedia Commons using the topic.
    Returns a list of image objects.
    """
    url = "https://commons.wikimedia.org/w/api.php"
    
    # Try multiple broad searches
    search_queries = [
        f"{topic} diagram",
        f"{topic} structure",
        f"{topic}"
    ]
    
    images = []
    
    for query in search_queries:
        if len(images) >= limit:
            break
            
        params = {
            "action": "query",
            "generator": "search",
            "gsrnamespace": 6,  # 6 = File namespace
            "gsrsearch": query,
            "gsrlimit": limit,
            "prop": "imageinfo",
            "iiprop": "url|extmetadata",
            "format": "json",
        }
        
        try:
            headers = {"User-Agent": "EduAccess-AI/1.0 (Educational Project)"}
            response = requests.get(url, params=params, headers=headers, timeout=5)
            data = response.json()
            
            pages = data.get("query", {}).get("pages", {})
            for page_id, page in pages.items():
                if len(images) >= limit:
                    break
                    
                imageinfo = page.get("imageinfo", [])
                if imageinfo:
                    info = imageinfo[0]
                    img_url = info.get("url")
                    
                    # Ensure it's not a duplicate
                    if img_url and img_url not in [img['url'] for img in images]:
                        # Skip audio and video files
                        if not any(img_url.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.svg', '.gif', '.webp']):
                            continue
                            
                        metadata = info.get("extmetadata", {})
                        raw_title = page.get("title", "")
                        clean_title = raw_title.replace("File:", "").split(".")[0].replace("_", " ")
                        
                        artist = metadata.get("Artist", {}).get("value", "Wikimedia Commons")
                        # Clean HTML from artist
                        artist = re.sub(r'<[^>]*>?', '', str(artist))
                        
                        images.append({
                            "url": img_url,
                            "title": clean_title,
                            "caption": f"Source: {artist}",
                            "what_it_shows": f"An educational visual related to {topic}.",
                            "teacher_explanation": f"Use this visual to help students understand the structure and concepts of {topic}."
                        })
        except Exception as e:
            logger.warning(f"Error fetching images for query '{query}': {e}")
            
    # If we couldn't find anything, return a fallback placeholder
    if not images:
        images.append({
            "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/No_image_available.svg/600px-No_image_available.svg.png",
            "title": f"{topic} Visual Not Found",
            "caption": "No image available on Wikimedia Commons.",
            "what_it_shows": "Placeholder Image",
            "teacher_explanation": "Could not automatically fetch a diagram for this topic."
        })
        
    return images
