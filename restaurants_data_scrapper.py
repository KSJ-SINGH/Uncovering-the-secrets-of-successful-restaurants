from bs4 import BeautifulSoup as bs
import pandas as pd
from path import check_dir
from selenium import webdriver
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import time

check_dir()  # This function is responsible for checking and changing the working directory of the project

homepage_url = "https://www.zomato.com/jabalpur/restaurants"

options = webdriver.EdgeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
driver = webdriver.Edge(EdgeChromiumDriverManager().install(), options= options)
driver.get(homepage_url)

time.sleep(1)  # Suspends the webpage for 1 seconds
scroll_pause_time = 2  # Time interval between two consecutive scrolls
screen_height = driver.execute_script("return window.screen.height;")  # extract the screen height of the webpage
i = 1

while True:
    # scroll a height of one screen at a time
    driver.execute_script("window.scrollTo(0, {screen_height}*{i});".format(screen_height=screen_height, i=i))
    i += 1
    time.sleep(scroll_pause_time)
    # update scroll height after each scroll
    scroll_height = driver.execute_script("return document.body.scrollHeight;")
    # Break the loop when the height to scroll to is larger than the total scroll height
    if (screen_height) * i > scroll_height:
        break

homepage_soup = bs(driver.page_source, "html.parser")

rest_names=[]
cuisines= []
price_per_person = []
locality = []
all_rest_page_url = []
delivery_rating = []
delivery_reviews = []
dining_rating = []
dining_reviews = []
timings = []
name_tags = homepage_soup.find_all("h4")

rest_homepage_url = "https://www.zomato.com"


for rest_name in name_tags[:len(name_tags)-1]:

    rest_names.append(rest_name.text)

    rest_page_tag = rest_name.parent.parent 

    rest_page_tag = rest_page_tag["href"][:-5] + "reviews"
    all_rest_page_url.append(rest_page_tag)

    price_tag = rest_name.parent.next_sibling.p.next_sibling.text
    price_per_person.append(price_tag)

    cuisine_tag = rest_name.parent.next_sibling.p.text
    cuisines.append(cuisine_tag)


for page_tags in all_rest_page_url:
    page_url = rest_homepage_url + page_tags
    driver.get(page_url)
    
    time.sleep(2)

    rest_page_soup = bs(driver.page_source, "html.parser")

    name_tag= rest_page_soup.find_all("h1")

    if len(name_tag) <=1:
        driver.refresh()

    try:
            
        location_tag = name_tag[1].parent.next_sibling.div.next_sibling.text
        locality.append(location_tag)

        time_tag = name_tag[1].parent.next_sibling.next_sibling.section.span.next_sibling.text
        timings.append(time_tag)

        delivery_rating_tag = name_tag[1].next_sibling.div.next_sibling.next_sibling.div.div.div.div.text
        delivery_rating.append(delivery_rating_tag)
        
        delivery_review_tag = name_tag[1].next_sibling.div.next_sibling.next_sibling.div.next_sibling.div.text
        delivery_reviews.append(delivery_review_tag)

        dining_review_tag = name_tag[1].next_sibling.div.div.next_sibling.div.text
        dining_reviews.append(dining_review_tag)

        dining_rating_tag = name_tag[1].next_sibling.div.div.div.div.div.text
        dining_rating.append(dining_rating_tag)
    
    except AttributeError:
        timings.append(None)
        delivery_rating.append(0)
        delivery_reviews.append(0)
        dining_reviews.append(0)
        dining_rating.append(0)

driver.close()

restaurants_df = pd.DataFrame({"name": rest_names, "cuisines": cuisines, "price_per_person": price_per_person, "location": locality, "timings" : timings, "delivery_rating": delivery_rating, "delivery_reviews": delivery_reviews, "dining_rating": dining_rating, "dining_reviews" : dining_reviews})
restaurants_df.to_csv("./Dataset/jabalpur_restaurants.csv")

