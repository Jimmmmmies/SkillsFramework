import requests
import os
from app.tools.base import tool
from app.exceptions import ToolException
from dotenv import load_dotenv
load_dotenv()

@tool("getweather", "Fetch current weather for a specified city.")
async def getweather(location: str) -> str:
    """
    Fetch current weather for a specified city.
    
    Args:
        location: City or region name, Chinese or English (e.g., "Beijing" or "北京").
    Returns:
         A dict with city name, weather description, and temperature in Celsius.
    """
    api_key = os.getenv("WEATHER_API_KEY")
    url = f"https://api.seniverse.com/v3/weather/now.json?key={api_key}&location={location}&language=zh-Hans&unit=c"
    
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        result = data["results"][0]
        weather = {
            "city": result["location"]["name"],
            "description": result["now"]["text"],
            "temperature": result["now"]["temperature"],
        }
        return weather
    
    raise ToolException(f"Failed to fetch weather, status code: {response.status_code}")