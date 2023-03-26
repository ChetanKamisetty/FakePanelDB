import os
import requests
from bs4 import BeautifulSoup
import time

# URL of the website to scrape
fonts_site = "https://fontmeme.com/fonts/korean-fonts-collection/"
# Start and end page numbers to scrape
start_page = 1
end_page = 8
# File path to save downloaded fonts
file_path = "D:\Fonts"
# User-Agent header for the HTTP requests
headers = {
    "User-Agent": "INSERT_YOUR_USER_AGENT"
}

# Function to scrape the website and download fonts
def scrape_site():
    # Loop over the pages to scrape
    for i in range(start_page, end_page+1):
        # Construct the URL of the current page
        url = f"{fonts_site}{i}/"

        try:
            # Send a HTTP request to the page
            page = requests.get(url, headers=headers)
            # Raise an exception if the response is not OK (status code 200)
            page.raise_for_status()
        except requests.exceptions.RequestException as e:
            # Print an error message and continue with the next page if the request fails
            print(f"Failed to scrape {url}: {str(e)}")
            continue

        # Parse the HTML of the page with BeautifulSoup
        soup = BeautifulSoup(page.text, "html.parser")
        # Find all the divs that contain the font download links
        downloads_pages = soup.find_all("div", {"class", "fontPreviewImageWrapper"})

        # Loop over the font download links
        for j, pg in enumerate(downloads_pages):
            # Parse the HTML of the link with BeautifulSoup
            inside = pg.decode_contents()
            inside = BeautifulSoup(inside, "html.parser").find("a")

            try:
                # Send a HTTP request to the font download page
                download_page = requests.get(inside['href'], headers=headers)
                # Raise an exception if the response is not OK (status code 200)
                download_page.raise_for_status()
            except requests.exceptions.RequestException as e:
                # Print an error message and continue with the next font if the request fails
                print(f"Failed to access download page {inside['href']}: {str(e)}")
                continue

            # Parse the HTML of the font download page with BeautifulSoup
            soup2 = BeautifulSoup(download_page.text, "html.parser")
            # Find the link to download the font
            dl_link = soup2.body.find(string="DOWNLOAD")

            if dl_link is None:
                # Print an error message and continue with the next font if the download link is not found
                print(f"Failed to find download link on page {inside['href']}")
                continue

            # Extract the download link from the onclick attribute of the "DOWNLOAD" button
            dl_link = dl_link.parent['onclick'][16:].replace("'", "").replace(";", "")
            print(dl_link)

            try:
                # Send a HTTP request to download the font file
                download_font = requests.get(dl_link, headers=headers)
                # Raise an exception if the response is not OK (status code 200)
                download_font.raise_for_status()
            except requests.exceptions.RequestException as e:
                # Print an error message and continue with the next font if the request fails
                print(f"Failed to download font from {dl_link}: {str(e)}")
                continue

            # Save the downloaded font file to disk
            with open(os.path.join(file_path, f"{i}_{j}.zip"), 'ab') as f:
                for chunk in download_font.iter_content(chunk_size=2048):
                    f.write(chunk)

            # Wait to not overload the site and downloads
            time.sleep(5)

        print(f"Finished scraping page {i}")

if __name__ == "__main__":
    scrape_site()