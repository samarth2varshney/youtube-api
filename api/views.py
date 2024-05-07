from rest_framework.views import APIView
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from rest_framework.response import Response
import time
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import NoSuchElementException
import json,os

chrome_driver_service = ChromeService(ChromeDriverManager().install())
chrome_options = Options()
# chrome_options.add_argument('--headless=new')
# chrome_options.add_argument('--disable-gpu')
# chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")

chrome_driver = webdriver.Chrome(service=chrome_driver_service, options=chrome_options)
chrome_driver.get('https://youtube.com')

# loadcookies/
class load_cookies(APIView):
    def get(self,request):

        cookies = request.data

        for cookie in cookies:
            chrome_driver.add_cookie(cookie)

        chrome_driver.refresh()
        
        return Response('success')

# signin/
class GoogleSignIn(APIView):
    def get(self,request):

        chrome_driver.get("https://accounts.google.com/ServiceLogin?hl=en&continue=https%3A%2F%2Fwww.youtube.com%2Fsignin%3Fhl%3Den%26feature%3Dsign_in_button%26app%3Ddesktop%26action_handle_signin%3Dtrue%26next%3D%252F&uilel=3&passive=true&service=youtube#identifier")

        email = request.query_params['email']
        password = request.query_params['password']

        WebDriverWait(chrome_driver, 15).until(
            EC.visibility_of_element_located((By.ID, 'identifierId'))
        )

        input = chrome_driver.find_element(By.ID, "identifierId")
        input.send_keys(email)

        WebDriverWait(chrome_driver, 15).until(
            EC.visibility_of_element_located((By.ID, 'identifierNext'))
        )

        next = chrome_driver.find_element(By.ID, "identifierNext")
        next.click()

        WebDriverWait(chrome_driver, 15).until(
            EC.visibility_of_element_located((By.NAME, 'Passwd'))
        )

        input = chrome_driver.find_element(By.NAME, 'Passwd')
        input.send_keys(password)

        chrome_driver.find_element(By.ID, "passwordNext").click()

        WebDriverWait(chrome_driver, 15).until(
            EC.visibility_of_element_located((By.ID, 'video-title-link'))
        )


        cookies = chrome_driver.get_cookies()

        return Response(cookies)

class main_page_links(APIView):
    def get(self, request):
        WebDriverWait(chrome_driver, 15).until(
        EC.visibility_of_element_located((By.ID, 'video-title-link'))
        )

        container = chrome_driver.find_elements(By.ID, "video-title-link")

        video_info = []

        count = 0

        for elements in container:
            try:
                link = extract(elements.get_attribute('href'))
                video_info.append({"videoId":link})
                count+=1
                
            except StaleElementReferenceException:
                container = chrome_driver.find_elements(By.ID, "video-title-link")
                continue
        
        print(count)

        return Response({"data":video_info})
    
class trending(APIView):
    def get(self, request):
        url = 'https://www.youtube.com/feed/trending'
        video_info = extract_youtube(url)   
        return Response(video_info)

class search_query(APIView):   
    def get(self, request):
        query = request.query_params['id']
        video_info = search_using_box(query)  
        return Response(video_info)

def extract_youtube(url):
    
    global chrome_driver
    
    chrome_driver.get(url)
    WebDriverWait(chrome_driver, 15).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, 'h3.title-and-badge'))
    )

    container = chrome_driver.find_elements(By.CSS_SELECTOR, "h3.title-and-badge")
    video_info = []

    for elements in container:
        link = elements.find_element(By.ID, 'video-title').get_attribute('href')
        title = elements.find_element(By.ID, 'video-title').text

        video_id = extract(link)
        if video_id != "":
            video_info.append({"video_id": video_id, "title": title})
        

    return video_info      

def extract(link):
    var = ""
    copy = False

    for char in link:
        if char == '&':
            break
        if copy:
            var += char
        if char == '=':
            copy = True

    return var 

def extract_video_info(a):
    
    views_index = a.find('views')

    if views_index == -1:
        return None

    i = views_index - 2
    view = ""

    while a[i] != ' ':
        view = a[i] + view
        i -= 1

    end = i

    while i >= 0:
        if a[i] == 'y' and a[i - 1] == 'b' and a[i - 2] == ' ':
            break
        i -= 1

    i += 2

    chname = a[i:end]

    i -= 3

    title = a[:i]

    return view, chname

def show_more():

    show_more_button = chrome_driver.find_elements(By.XPATH,'//button[contains(@aria-label,"Show more")]')

    for button in show_more_button:
        button.click()

def clear_search_box():
    try:
        search_box = chrome_driver.find_element(By.CSS_SELECTOR, "input#search")
        search_box.clear()
    except StaleElementReferenceException:
        time.sleep(1)
        clear_search_box()

def search_using_box(query):
    
    WebDriverWait(chrome_driver, 15).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, 'ytd-searchbox'))
    )

    clear_search_box()

    container = chrome_driver.find_element(By.CSS_SELECTOR, "ytd-searchbox")
    container.send_keys(query)

    WebDriverWait(chrome_driver, 15).until(
        EC.visibility_of_element_located((By.ID, "search-icon-legacy"))
    )

    button = chrome_driver.find_element(By.ID, "search-icon-legacy")
    button.click()

    WebDriverWait(chrome_driver, 15).until_not(
        EC.visibility_of_element_located((By.CSS_SELECTOR, 'h3.title-and-badge'))
    )

    WebDriverWait(chrome_driver, 15).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, 'h3.title-and-badge'))
    )

    container = chrome_driver.find_elements(By.CSS_SELECTOR, "h3.title-and-badge")

    video_info = []

    for elements in container:
        try:
            link = elements.find_element(By.ID, 'video-title').get_attribute('href')
            title = elements.find_element(By.ID, 'video-title').text
            
            video_id = extract(link)
            if video_id != "":
                video_info.append({"video_id": video_id, "title": title})

        except StaleElementReferenceException:
            container = chrome_driver.find_elements(By.CSS_SELECTOR, "h3.title-and-badge")
            continue

    chrome_driver.back()    

    return video_info 