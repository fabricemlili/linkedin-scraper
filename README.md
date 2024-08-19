# LinkedIn Scraper

A simple Python script to scrape content and metadata from posts on the [LinkedIn](https://www.linkedin.com/feed/) accounts of individuals and companies. It utilizes the selenium library for automating web browser interaction, and BeautifulSoup for parsing HTML content. This script can help gather valuable insights from LinkedIn posts, such as post content, engagement metrics (likes, comments, shares), and author information.

## Prerequisites

Before running the script, make sure you have the following dependencies installed:

- Python 3
- beautifulsoup4
- selenium
- pandas
- python-dotenv
- python-dateutil

Install the required Python packages using the following command:

```bash
pip install selenium beautifulsoup4 pandas python-dotenv python-dateutil
```

## Setup

##### 1) WebDriver Installation:
You need ChromeDriver for Selenium. Download it from here and ensure it's accessible via your system's PATH.

##### 2) Environment Variables:
Create a .env file in the same directory as the script with your LinkedIn credentials:
```bash
username="your_linkedin_username"
password="your_linkedin_password"
```

##### 3) Links File:
Create a text file containing the URLs of the LinkedIn profiles and company pages you want to scrape, or save them in the default text file called `links.txt`. Each URL must be on a new line and take one of the following forms:

- Company: https://www.linkedin.com/company/adidas/posts/?feedView=all

- Person: https://www.linkedin.com/in/williamhgates/recent-activity/all/

## Usage
To use the script, follow these steps:

###### 1. Clone the repository or download the script.

```bash
git clone https://github.com/fabricemlili/journalducoin-scraper.git
```
###### 2. Navigate to the script's directory.
```bash
cd journalducoin-scraper
```
###### 3. Run the script by executing the following command in your terminal:
```bash
python linkedin_scraper.py -f <path_of_text_file>
```
Here, `-f` specifies the text file containing LinkedIn URLs. The default is `links.txt`.

## Output

The scraped content will be saved to a csv file named `linkedin_posts.csv` in the same directory as the script. You can find five different types of data inside:
- Date: From post relative date.
- Reactions Count: Number of reactions to each post.
- Comments Count: Number of comments on each post.
- Reposts Count: Number of reposts of each post.
- Text: Content of each post.

## Future Improvements
While the current script is functional, several improvements are planned to enhance its performance and capabilities:

1. Include additional metadata such as post URLs and additional author information

2. Improve date extraction to obtain the actual date of the article. For the moment, the only solution found is to use the post's URL, which contains the date in a special format.

3. Scrape the user's LinkedIn feed.

## Notes

- WebDriver Configuration: The script uses the default Chrome WebDriver. You can customize Chrome options if needed.
- LinkedIn Changes: LinkedIn's HTML structure or login process changes may require updates to the script.
- Rate Limiting: Frequent or extensive scraping can lead to human verification (with a schema to solve) at the very least, and temporary account restrictions by LinkedIn at worst.

## Author
Fabrice Mlili

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
