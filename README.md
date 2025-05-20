# Concert_Ticket_LINE_Bot 
This project is a Python-based system that automatically searches for upcoming concerts in Taiwan for specific artists. 
It uses web scraping (e.g., KKTIX) and Google Custom Search to retrieve event details and promotional images. 
The bot checks for updates and notifies users—such as through a LINE Bot—when new concert information becomes available. 
It supports artist tracking, data filtering, and media integration to deliver timely, accurate concert updates.

## How to Run
```
python app.py
```

## TODO list :heavy_check_mark: 
Idx | Content | State | Note
:------------ | :-------------| :-------------| :-------------
1 | Construct the basic framework about how the whole code works | :heavy_check_mark: | 
2 | Make sure all the information are accurate and provide relevent pictures | :heavy_check_mark: | Still need to improve on code efficiency
3 | Linked the program with LINE BOT | :heavy_check_mark: | 
## LOG
### 5/20/2025
- Implemented fallback image handling using Cloudinary
    1. Use Cloudinary for more control and reliability
    2. Added a upload_to_cloudinary(image_url) function that validates content type is image/* before uploading
- Update get_best_concert_info_line() to:
    1. Automatically upload fetched images to Cloudinary
    2. Integrate fallback logic and prevent invalid or broken image URLs from being used
 - Linked the code with the LINE Bot and enhanced user experience
    1. Added intermediate reply: "🔍 查詢中，請稍候..." when user sends a query
    2. Built and implemented a visually styled Flex Message card
### 5/17/2025
- Installed Git system
- Wrote a function choose_best_concert_info() that:
    1. Sends multiple concert data/location candidates per artist to ChatGPT
    2. Uses a Chinese-language system prompt to let ChatGPT pick the most likely correct one
    3. Ensures JSON-formatted responses for easier parsing
- Wrote the function get_concerts_from_google(artist) to:
    1. Use Custom Search API to pull top 5 links
    2. Extract title, link, and snippet from each
- Wrote extract_information(text) using regex to:
    1. Identify concert dates
    2. Detect locations (Taipei, Kaohsiung, Taichung, etc.)
- Built get_concert_details(artist) to combine title/snippet info with location and optional image
- Added search_concert_image(artist) using Google image search to find concert posters
### 5/15/2025
- Construct a basic program that allows user to receive information about the specific singers
---


  


## References
1. 

