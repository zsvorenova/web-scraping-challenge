from splinter import Browser
from bs4 import BeautifulSoup as bs
import pandas as pd
import time


def init_browser():
    # @NOTE: Replace the path with your actual path to the chromedriver
    executable_path = {"executable_path": "chromedriver"}
    return Browser("chrome", **executable_path, headless=False)

   
def scrape():
    browser = init_browser()

    # create mars_data dict that we can insert into mongo
    mars_data = {}

    # LATEST MARS NEWS
    url_news = 'https://mars.nasa.gov/news'
    browser.visit(url_news)
    time.sleep(3)
    # Scrape page into Soup
    html = browser.html
    soup = bs(html, "html.parser")
    # find and save the latest news
    latest_news=soup.find_all('div', class_="list_text")[0]
    news_title=latest_news.find(class_="content_title").text.strip()
    news_p=latest_news.find(class_="article_teaser_body").text.strip()

    # MARS FEATURED IMAGE
    url_images='https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url_images)
    time.sleep(1)
    # Scrape page into Soup
    html = browser.html
    soup = bs(html, "html.parser")
    # find and save the Featured Image href nad full link
    featured_image=soup.find('article').find('footer').a['data-fancybox-href']
    featured_image_url="https://www.jpl.nasa.gov/"+featured_image

    # MARS FACTS
    url_facts = 'https://space-facts.com/mars/'
    tables=pd.read_html(url_facts)
    time.sleep(1)
    mars_facts = tables[0]
    mars_facts.columns = ['Description', 'Mars']
    mars_facts.set_index('Description', inplace=True)
    facts_html=mars_facts.to_html().replace('\n', '').replace('dataframe','table table-bordered table-striped table-sm').replace('border="1"','')

    # MARS HEMISPHERES
    url_hems = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    base_url='https://astrogeology.usgs.gov'
    browser.visit(url_hems)
    time.sleep(1)
    html = browser.html
    # Parse HTML with Beautiful Soup
    soup = bs(html, 'html.parser')

    # get links for each hemisphere page:
    results=soup.find('div', class_="collapsible results").find_all('div', class_="item")
    hem_url_list=[]
    for result in results:
        hem_link=result.find('a')['href']
        hem_url_list.append(base_url+hem_link)

    hemisphere_image_urls = []
    for hem_url in hem_url_list:
        # open each page and parse HTML with Beautiful Soup
        browser.visit(hem_url)
        time.sleep(1)
        html = browser.html
        soup = bs(html, 'html.parser')
        
        #find image link and title
        img_link=soup.find('img', class_="wide-image")['src']
        img_url=base_url+img_link
        title = soup.find('h2', class_="title").text.strip(' Enhanced')
            
        # create a dictionairy and append it to list of hemisphere image urls
        hem_data = {
            'title': title,
            'img_url': img_url,
        }
        hemisphere_image_urls.append(hem_data)

    # Store data in a dictionary
    mars_data = {
        "news_title": news_title,
        "news_p": news_p,
        "featured_image_url": featured_image_url,
        "facts_html": facts_html,
        "hemisphere_image_urls": hemisphere_image_urls
    }

    # Close the browser after scraping
    browser.quit()

    # Return results
    return mars_data



    

   
