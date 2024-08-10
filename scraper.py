from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup as bs
import pandas as pd
import time
from dotenv import load_dotenv
import os
import argparse
import re
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

# Function to process date offsets
def process_date(howlong):
    # Use regex to extract the numeric and unit parts from the input string (e.g., '2d')
    match = re.compile(r"(\d+)([a-zA-Z]+)").match(howlong)
    offset_value = int(match.group(1))  # Extract the numeric part (e.g., 2)
    offset_unit = match.group(2)        # Extract the unit part (e.g., 'd' for days)
    
    today = datetime.today()  # Get the current date and time
    
    # Determine the timedelta based on the unit of time
    if offset_unit == 'm':
        delta = timedelta(minutes=offset_value)
    elif offset_unit == 'h':
        delta = timedelta(hours=offset_value)
    elif offset_unit == 'd':
        delta = timedelta(days=offset_value)
    elif offset_unit == 'w':
        delta = timedelta(weeks=offset_value)
    elif offset_unit == 'mo':
        delta = relativedelta(months=offset_value)
    elif offset_unit == 'yr':
        delta = relativedelta(years=offset_value)
    else:
        raise ValueError("Unsupported unit in date offset string")  # Handle unsupported units
    
    # Calculate the new date by subtracting the delta from the current date
    new_date = today - delta
    return new_date.strftime('%Y-%m-%d')  # Return the new date as a string in 'YYYY-MM-DD' format

# Function to scrape LinkedIn posts from a list of URLs
def scrape_linkedin(file_of_links):
    load_dotenv()  # Load environment variables from a .env file
    username = os.getenv("username")  # Get LinkedIn username from environment variables
    password = os.getenv("password")  # Get LinkedIn password from environment variables

    # Read URLs from the file
    with open(file_of_links, 'r') as file:
        url_pages = file.readlines()  # Read each line as a URL

    # Set up Chrome options and initialize the WebDriver
    chrome_options = Options()
    browser = webdriver.Chrome()  # You can add options if needed
    browser.maximize_window()  # Maximize the browser window

    # Navigate to LinkedIn login page
    browser.get('https://www.linkedin.com/login?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin')

    # Enter username and password to log in
    elementID = browser.find_element(By.ID, "username")
    elementID.send_keys(username)
    elementID = browser.find_element(By.ID, "password")
    elementID.send_keys(password)
    elementID.submit()  # Submit the login form
    time.sleep(20)  # Wait for the login to complete

    # Iterate over each URL to scrape data
    for url_page in url_pages:
        url_page = url_page.strip()  # Remove any surrounding whitespace
        if not url_page:
            continue  # Skip empty lines

        browser.get(url_page)  # Open the URL
        current_url = browser.current_url

        url_parts = current_url.split("/")  # Split the URL to analyze its parts
        
        # Check URL structure and determine account type and name
        if len(url_parts) < 4:
            print(f"The URL {url_page} is not structured as expected.")
            continue

        last_part_url = url_parts[-2]

        if last_part_url == "all":
            account_type = 'individual'
            account_name = url_parts[-4].replace('-', ' ').title()
        elif last_part_url == "posts":
            account_type = 'company'
            account_name = url_parts[-3].replace('-', ' ').title()
        elif last_part_url == "?feedView=all":
            account_type = 'company'
            account_name = url_parts[-4].replace('-', ' ').title()
        else:
            print(f"The URL {url_page} is not related to the webpage of posts from a company or an individual.")
            continue

        # Set up scrolling parameters
        SCROLL_PAUSE_TIME = 1  # Time to wait after each scroll
        MAX_SCROLLS = False  # Set to an integer to limit the number of scrolls

        SCROLL_COMMAND = "window.scrollTo(0, document.body.scrollHeight);"  # JavaScript command to scroll to the bottom of the page
        GET_SCROLL_HEIGHT_COMMAND = "return document.body.scrollHeight"  # JavaScript command to get the current scroll height

        last_height = browser.execute_script(GET_SCROLL_HEIGHT_COMMAND)  # Get initial page height
        scrolls = 0
        no_change_count = 0

        # Scroll until reaching the bottom of the page or no new content is found
        while True:
            browser.execute_script(SCROLL_COMMAND)  # Execute the scroll command

            time.sleep(SCROLL_PAUSE_TIME)  # Wait for new content to load

            new_height = browser.execute_script(GET_SCROLL_HEIGHT_COMMAND)  # Get the new page height
            
            # Count how many times the height hasn't changed
            no_change_count = no_change_count + 1 if new_height == last_height else 0
            
            # Stop scrolling if there's no change or the maximum number of scrolls is reached
            if no_change_count >= 3 or (MAX_SCROLLS and scrolls >= MAX_SCROLLS):
                break
            
            last_height = new_height  # Update the last height
            scrolls += 1

        # Parse the page source with BeautifulSoup
        page_source = browser.page_source
        linkedin_soup = bs(page_source.encode("utf-8"), "html.parser")
        
        # Find all posts based on account type
        if account_type == 'company':     
            posts = linkedin_soup.find_all("div", {"class": "ember-view occludable-update"})
        else:
            posts = linkedin_soup.find_all("li", {"class": "profile-creator-shared-feed-update__container"})

        # Initialize lists to store post data
        reactions_counts = []
        comments_counts = []
        reposts_counts = []
        posts_texts = []
        dates = []

        # Extract data from each post
        for post in posts:
            howlong_container = post.find_all("span", {"class": "update-components-actor__sub-description text-body-xsmall t-black--light"})
            des_container = post.find_all("span", {"class": "break-words tvm-parent-container"})
            reactions_count_container = post.find_all("span", {"class": "social-details-social-counts__reactions-count"})
            comments_count_container = post.find_all("button", {"class": "t-black--light social-details-social-counts__count-value social-details-social-counts__count-value-hover t-12 hoverable-link-text social-details-social-counts__link"})
            reposts_count_container = post.find_all("button", {"class": "ember-view t-black--light social-details-social-counts__count-value-hover t-12 hoverable-link-text social-details-social-counts__link"})
            
            # Extract and clean reaction, comment, and repost counts
            reactions_count = reactions_count_container[0].get_text(strip=True).replace(',', '') if reactions_count_container else 0
            comments_count = comments_count_container[0].get_text(strip=True).replace(' comments', '').replace(' comment', '').replace(',', '') if comments_count_container else 0
            reposts_count = reposts_count_container[0].get_text(strip=True).replace(' reposts', '').replace(' repost', '').replace(',', '') if reposts_count_container else 0
            
            # Extract post text
            post_text = des_container[0].get_text(strip=True) if des_container else ''
            howlong = howlong_container[0].get_text(strip=True).split(' ')[0] if howlong_container else None

            # Process the date if available
            if howlong:
                date = process_date(howlong)
                reactions_counts.append(reactions_count)
                comments_counts.append(comments_count)
                reposts_counts.append(reposts_count)
                posts_texts.append(post_text)
                dates.append(date)

        # Create a DataFrame and save it to a CSV file
        df = pd.DataFrame({
            "Nom": account_name,
            "Account Type": account_type,
            'Date': dates,
            'Reactions Count': reactions_counts,
            'Comments Count': comments_counts,
            'Reposts Count': reposts_counts,
            'Text': posts_texts
        })

        df.to_csv('linkedin_posts.csv', mode='a', header=not os.path.exists('linkedin_posts.csv'), index=False)

        print(f"Data for {account_name} saved successfully.")

    browser.quit()  # Close the browser

    # Remove duplicate rows from the CSV file
    df = pd.read_csv('linkedin_posts.csv')
    df_cleaned = df.drop_duplicates()
    df_cleaned.to_csv('linkedin_posts.csv', index=False)

# Entry point of the script
if __name__ == "__main__":
    # Set up command-line argument parser
    parser = argparse.ArgumentParser(description='Scrape content and metadata from posts on the LinkedIn accounts of individuals and companies.')
    
    # Define command-line argument for the file containing links to scrape
    parser.add_argument('-f', '--txtfile', type=str, default='links.txt', help='Text file with links to scrape')
    
    # Parse the command-line arguments and call the scraping function
    scrape_linkedin(parser.parse_args().txtfile)