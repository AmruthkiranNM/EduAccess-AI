import requests
import logging
import re
import os
import uuid

logger = logging.getLogger(__name__)

# Base directory for caching images
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
CACHE_DIR = os.path.join(BASE_DIR, 'frontend', 'static', 'cache', 'images')

# Ensure cache directory exists
os.makedirs(CACHE_DIR, exist_ok=True)

def verify_and_cache_image(img_url, img_ext):
    """
    Downloads and verifies an image. If valid, caches it locally and returns the local URL.
    Returns None if verification fails.
    """
    try:
        # Request with a stream to only download if it's a valid image
        headers = {"User-Agent": "EduAccess-AI/1.0 (Educational Project)"}
        response = requests.get(img_url, headers=headers, stream=True, timeout=5)
        
        # 1. Verify HTTP Status
        if response.status_code != 200:
            logger.warning(f"Image verification failed: HTTP {response.status_code} for {img_url}")
            return None
            
        # 2. Verify Content-Type
        content_type = response.headers.get('Content-Type', '')
        if not content_type.startswith('image/'):
            logger.warning(f"Image verification failed: Invalid Content-Type '{content_type}' for {img_url}")
            return None
            
        # 3. Verify Size > 0 (if provided in headers)
        content_length = response.headers.get('Content-Length')
        if content_length is not None and int(content_length) == 0:
            logger.warning(f"Image verification failed: Empty image size for {img_url}")
            return None
            
        # Generate a unique filename
        filename = f"{uuid.uuid4().hex}{img_ext}"
        filepath = os.path.join(CACHE_DIR, filename)
        
        # Download and save the image
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
                
        # Return the local URL path for the frontend
        return f"/static/cache/images/{filename}"
        
    except requests.RequestException as e:
        logger.warning(f"Network error during image verification for {img_url}: {e}")
        return None
    except Exception as e:
        logger.warning(f"Unexpected error caching image {img_url}: {e}")
        return None

def fetch_educational_images(topic, limit=4):
    """
    Fetches curated educational images from Wikimedia Commons using the topic.
    Downloads, verifies, and caches them locally before returning.
    """
    url = "https://commons.wikimedia.org/w/api.php"
    
    # Try multiple broad searches
    search_queries = [
        f"{topic} diagram",
        f"{topic} structure",
        f"{topic} illustration",
        f"{topic}"
    ]
    
    images = []
    seen_urls = set()
    
    for query in search_queries:
        if len(images) >= limit:
            break
            
        params = {
            "action": "query",
            "generator": "search",
            "gsrnamespace": 6,  # 6 = File namespace
            "gsrsearch": query,
            "gsrlimit": limit * 2, # Request more to account for failed verifications
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
                    
                    if img_url and img_url not in seen_urls:
                        # Skip audio and video files, extract extension
                        valid_extensions = ['.png', '.jpg', '.jpeg', '.svg', '.gif', '.webp']
                        img_ext = next((ext for ext in valid_extensions if img_url.lower().endswith(ext)), None)
                        
                        if not img_ext:
                            continue
                            
                        # Verify and cache the image
                        logger.info(f"Verifying candidate image: {img_url}")
                        local_url = verify_and_cache_image(img_url, img_ext)
                        
                        if local_url:
                            seen_urls.add(img_url)
                            metadata = info.get("extmetadata", {})
                            raw_title = page.get("title", "")
                            clean_title = raw_title.replace("File:", "").split(".")[0].replace("_", " ")
                            
                            artist = metadata.get("Artist", {}).get("value", "Wikimedia Commons")
                            artist = re.sub(r'<[^>]*>?', '', str(artist))
                            
                            images.append({
                                "url": local_url,
                                "title": clean_title,
                                "caption": f"Source: {artist}",
                                "what_it_shows": f"An educational visual related to {topic}.",
                                "teacher_explanation": f"Use this visual to help students understand the structure and concepts of {topic}."
                            })
                            logger.info(f"Successfully cached image for '{topic}': {local_url}")
        except Exception as e:
            logger.warning(f"Error fetching images for query '{query}': {e}")
            
    # If we couldn't find anything, return an empty array, the frontend will handle the fallback
    if not images:
        logger.warning(f"No valid images found for topic '{topic}'.")
        
    return images
