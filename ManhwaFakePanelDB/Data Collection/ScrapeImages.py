import requests
from bs4 import BeautifulSoup
import time
from PIL import Image
import sys


# Main domain of the site we're going to scrape images from.
main_domain = "https://danbooru.donmai.us"
file_path = "D:\ManhwaImages"

# URL For images, replace with the first page of the tag you want.
# (Click random page number then click page 1 and copy URL.)

def page_info(page):
    # URL For images, replace with the first page of the tag you want.
    # (Click random page number then click page 1 and copy URL.)
    images_url = f"https://danbooru.donmai.us/posts?page={page}&tags=official_wallpaper+"

    r = requests.get(url=images_url)

    soup = BeautifulSoup(r.text, 'html.parser')

    # Get Page Numbers: Subject to change until a more
    # reliable way is found
    first_page = soup.find('span', {"class", "paginator-current font-bold"}).text
    a_span = soup.find_all('a', {"class", "paginator-page desktop-only"})
    last_page = a_span[4].text

    # Getting the images: Also subject to change.
    articles = soup.find_all('a', {"class", "post-preview-link"})
    img_per_page = len(articles)

    return { "first_page": first_page,
             "last_page": last_page,
             "articles": articles,
             "img_per_page": img_per_page
            }

def scrape_images(compression):
    for p in range(int(f_page), int(l_page)):
        page = page_info(p)
        sys.stdout.write(f"\rCurrently Scraping page {p}")
        sys.stdout.flush()
        for img in range(page['img_per_page']):
            # Goes to each image's page and grabs big image URL
            get_img = requests.get(url=f"{main_domain}{page['articles'][img]['href']}")
            img_soup = BeautifulSoup(get_img.text, 'html.parser')
            try:
                img_url = img_soup.find("a", {"class", "image-view-large-link"})['href']
            except TypeError as e:
                if str(e) == "'NoneType' object is not subscriptable":
                    continue
                else:
                    print(str(e))

            img_url = img_soup.find("a", {"class", "image-view-large-link"})['href']
            
            # Download the image
            dl_img = requests.get(url=img_url)

            # Save the image in your file path (change file path to where you want to store)
            with open(f"{file_path}\{p}_{img}_image.png", 'wb') as f:
                f.write(dl_img.content)
                # Compress Image to take less space
                if compression:
                    img = Image.open(f"{file_path}\{p}_{img}_image.png")
                    img.save("image-file-compressed",
                            "PNG",
                            optimize = True,
                            quality = 10)

            time.sleep(1)

p_info = page_info(1)

f_page = p_info['first_page']
l_page = p_info['last_page']

scrape_images(compression=False)
