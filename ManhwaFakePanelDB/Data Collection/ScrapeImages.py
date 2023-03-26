import os
import requests
from bs4 import BeautifulSoup
import time
from PIL import Image
import sys


# Main domain of the site we're going to scrape images from.
main_domain = "https://danbooru.donmai.us"
file_path = r"D:\ManhwaImages"


def page_info(page):
    # URL for images, replace with the first page of the tag you want.
    images_url = f"{main_domain}/posts?page={page}&tags=official_wallpaper+"

    r = requests.get(url=images_url)

    soup = BeautifulSoup(r.text, 'html.parser')

    # Get page numbers
    try:
        first_page = soup.find('span', {"class", "paginator-current font-bold"}).text
        a_span = soup.find_all('a', {"class", "paginator-page desktop-only"})
        last_page = a_span[4].text
    except AttributeError:
        print(f"Failed to retrieve page numbers for page {page}")
        return None

    # Get the images
    articles = soup.find_all('a', {"class", "post-preview-link"})
    img_per_page = len(articles)

    return {"first_page": first_page,
            "last_page": last_page,
            "articles": articles,
            "img_per_page": img_per_page}


def scrape_images(compression=False):
    p_info = page_info(1)

    if p_info is None:
        return

    f_page = p_info['first_page']
    l_page = p_info['last_page']

    for p in range(int(f_page), int(l_page)):
        page = page_info(p)

        if page is None:
            continue

        sys.stdout.write(f"\rCurrently scraping page {p}")
        sys.stdout.flush()

        for img in range(page['img_per_page']):
            # Go to each image's page and grab the big image URL
            try:
                get_img = requests.get(url=f"{main_domain}{page['articles'][img]['href']}")
                img_soup = BeautifulSoup(get_img.text, 'html.parser')
                img_url = img_soup.find("a", {"class", "image-view-large-link"})['href']
            except (TypeError, AttributeError):
                continue

            # Download the image
            try:
                dl_img = requests.get(url=img_url)
            except requests.exceptions.RequestException as e:
                print(f"Failed to download image {img} on page {p}: {str(e)}")
                continue

            # Save the image in your file path
            try:
                os.makedirs(file_path, exist_ok=True)
                file_name = f"{p}_{img}_image.png"
                file_path_name = os.path.join(file_path, file_name)
                with open(file_path_name, 'wb') as f:
                    f.write(dl_img.content)

                # Compress the image to take less space (use ONLY if needed)
                if compression:
                    c_img = Image.open(f"{file_path}\{p}_{img}_image.png")
                    c_img.save(f"{file_path}\{p}_{img}_image.png",
                             "PNG",
                             optimize=True,
                             quality=10)
            except IOError as e:
                print(f"Failed to save image {img} on page {p}: {str(e)}")
                continue

            time.sleep(1)


if __name__ == "__main__":
    scrape_images(compression=False)
