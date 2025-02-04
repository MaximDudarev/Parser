import json

import undetected_chromedriver as uc
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from curl_cffi import requests
from bs4 import BeautifulSoup

def get_cookies():       # возвращает куки и user-агента
    options = uc.ChromeOptions()
    options.headless = True

    with uc.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options) as driver:
        driver.implicitly_wait(60)
        driver.get('https://ozon.by')
        driver.find_element(By.CSS_SELECTOR, '#stickyHeader')
        user_agent = driver.execute_script('return navigator.userAgent')
        cookies = driver.get_cookies()

    cookies_dict = {i['name']:i['value'] for i in cookies}
    return user_agent, cookies_dict

user_agent, cookies_dict = get_cookies()

def parser_ozon(index):
    response = requests.get(f"https://ozon.by/product/{index}/?oos_search=false", cookies=cookies_dict, headers={
        "user-agent": user_agent
    })
    soup = BeautifulSoup(response.text, 'lxml')
    data = json.loads(soup.find('script', type='application/ld+json').string)

    price = data.get('offers')
    price = 'Не указана' if price is None else price.get('price') + ' ' + price.get('priceCurrency')

    rating = data.get('aggregateRating')
    rating = 0 if rating is None else rating.get('ratingValue')

    images = []
    class_img = " ".join(soup.find('div', class_='container c').find_all('img')[1]['class'])

    for img in soup.find_all('img', class_=class_img):
        src = img['src'].split('/')
        src[-2] = src[-2] + '00'
        images.append('/'.join(src))

    finally_dict = {'rating': rating, 'images': images, 'price': price}
    with open('output_file.json', 'w', encoding='utf-8') as file:
        json.dump(finally_dict, file, indent=4, ensure_ascii=False)
    return finally_dict

if __name__ == "__main__":
    print(parser_ozon(326478173))