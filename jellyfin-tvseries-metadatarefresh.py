import requests
import time
import langid
import os
import urllib3
import socket

userid = os.getenv("USERID")
token = os.getenv("TOKEN")
host = os.getenv("HOST")
protocol = os.getenv("PROTOCOL", "http")
target_confidence = os.getenv("TARGET_CONFIDENCE", 0.75)
target_lang = os.getenv("TARGET_LANG", "de")
max_connection_retries = os.getenv("CONNECTION_RETRIES", 3)
delay_between_retries = os.getenv("CONNECTION_ERROR_DELAY", 30)
force_episodes = os.getenv("FORCE_EPISODES", True)

error = 0

if not userid:
    print("Please set USERID")
    error = 1

if not token:
    print("Please set TOKEN")
    error = 1

if not host:
    print("Please set HOST")
    error = 1

if error:
    exit(1)


api_url=f"{protocol}://{host}"
headers =  {
    "Content-Type":"application/json",
    "Authorization": f"MediaBrowser Token=\"{token}\""
}

item_endpoint = "/Items"

DEBUG = 0
INFO = 1

def log_debug(text: str = "", end="\n"):
    if DEBUG:
        print(text, end=end)

def log_info(text: str = "", end="\n"):
    if INFO:
        print(text, end=end)

def log_error(text: str):
    print(text)

def get(url: str):
    attempts = 0
    while attempts < max_connection_retries:
        try:
            response = requests.get(url, headers=headers)
            return response
        except (requests.exceptions.ConnectionError, urllib3.exceptions.MaxRetryError, urllib3.exceptions.NameResolutionError, socket.gaierror) as e:
            attempts += 1
            if attempts < max_connection_retries:
                log_info(f"Connection error occurred. Attempt {attempts} of {max_connection_retries}. Retrying after {delay_between_retries} second.")
                time.sleep(delay_between_retries)
            else:
                log_error(f"Connection error occurred. Attempt {attempts} of {max_connection_retries}. Aborting.")
                raise e

def post(url: str):
    attempts = 0
    while attempts < max_connection_retries:
        try:
            response = requests.post(url, headers=headers)
            return response
        except (requests.exceptions.ConnectionError, urllib3.exceptions.MaxRetryError, urllib3.exceptions.NameResolutionError, socket.gaierror) as e:
            attempts += 1
            if attempts < max_connection_retries:
                log_info(f"Connection error occurred. Attempt {attempts} of {max_connection_retries}. Retrying after {delay_between_retries} second.")
                time.sleep(delay_between_retries)
            else:
                log_error(f"Connection error occurred. Attempt {attempts} of {max_connection_retries}. Aborting.")
                raise e

def getItemDetails(itemId: str):
    return get(F"{api_url}/Users/{userid}/Items/{itemId}")

def refreshItem(itemId: str):
    return post(F"{api_url}{item_endpoint}/{itemId}/Refresh?Recursive=true&ImageRefreshMode=FullRefresh&MetadataRefreshMode=FullRefresh&ReplaceAllImages=true&RegenerateTrickplay=true&ReplaceAllMetadata=true")

def refreshSeries(itemId: str, name: str):
    if not force_episodes:
        refreshItem(itemId)
        log_debug(f"Refreshed {name}, now getting Episodes.")
    else:
        answer = input(f"Checking episodes of {name}. Press any key to continue or 's' to skip.")
        if answer == 's':
            return
        
    # get episodes of the series
    episodes_response = get(F"{api_url}/Shows/{itemId}/Episodes")
    episodes_body = episodes_response.json()
    for episode in episodes_body["Items"]:
        name = episode["Name"]
        id = episode["Id"]
        episode_details_response = getItemDetails(id)
        episode_details_body = episode_details_response.json()
        answer = confidence_or_question(episode_details_body)
        if answer == 'y':
            response = refreshItem(id)
            log_info("  refreshed!")
            time.sleep(1)
        elif answer == 's':
            log_info(" skipped Series.")
            return
        


root_items_response = get(F"{api_url}{item_endpoint}")

if root_items_response.status_code != 200:
    log_error(f"Status code: {root_items_response.status_code}")
    exit(1)

responsebody = root_items_response.json()

def get_highest_ranked_language_from_overview(item_body):
    overview = item_body.get("Overview", "")
    log_info("======================")
    log_info(overview)
    log_info("======================")
    
    all_languages = langid.rank(overview)
    language, firstscore = all_languages[0]
    _, secondscore = all_languages[1]
    confidence_difference = firstscore / secondscore
    log_info(f"| {language} | {confidence_difference} |")
    return language, confidence_difference

def confidence_or_question(item_body):
    language, confidence_difference = get_highest_ranked_language_from_overview(item_body)
    if language == target_lang and confidence_difference > target_confidence:
        log_info(f"Enough confidence ({confidence_difference}) that the language is {language}. Skipping.")
        return 
    else:
        answer = input("Refresh item?")
        return answer

def processItem(item):
    if item["Type"] == "Folder":
        log_debug(f"{item["Type"]}: {item["Name"]}", end=" ")
        log_debug()
        getChildItemsResponse = get(f"{api_url}{item_endpoint}?parentId={item["Id"]}")
        getChildItemsBody = getChildItemsResponse.json()
        for childItem in getChildItemsBody["Items"]:
            processItem(childItem)
        
        return
    
    if item["Type"] == "Series":
        log_info(f"Serie: {item["Id"]} {item["Name"]}", end=" ")
        log_info()
        seriesDetails = getItemDetails(item["Id"])
        seriesDetailsBody = seriesDetails.json()

        if confidence_or_question(seriesDetailsBody) == 'y' or force_episodes:
            refreshSeries(item["Id"], item["Name"])
            log_info("  refreshed!")
            time.sleep(1)
        
        log_info("======================")
        return
    log_debug(f"{item["Type"]}: {item["Name"]}", end=" ")
    log_debug("Skipping.")
        

for parentItem in responsebody["Items"]:
    processItem(parentItem)