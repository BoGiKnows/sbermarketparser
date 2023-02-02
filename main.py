from bs4 import BeautifulSoup
import pickle
import undetected_chromedriver as uc
import csv


url = 'https://sbermegamarket.ru/catalog/noutbuki/page-'
MAIN_URL = 'https://sbermegamarket.ru'


class SeleniumClass:

    def __init__(self, cookies_file_path='chrome/cookies.pkl', cookies_websites=['https://sbermegamarket.ru']):
        options = uc.ChromeOptions()
        options.add_argument('--headless=new')
        self.cookies_file_path = cookies_file_path
        self.cookies_websites = cookies_websites
        self.driver = uc.Chrome(options=options)
        try:
            # load cookies for given websites
            cookies = pickle.load(open(self.cookies_file_path, "rb"))
            for website in self.cookies_websites:
                self.driver.get(website)
                for cookie in cookies:
                    self.driver.add_cookie(cookie)
                self.driver.refresh()
        except Exception as e:
            # it'll fail for the first time, when cookie file is not present
            print(str(e))
            print("Error loading cookies")

    def save_cookies(self):
        # save cookies
        cookies = self.driver.get_cookies()
        pickle.dump(cookies, open(self.cookies_file_path, "wb"))

    def links_to_goods(self, page):
        soup = BeautifulSoup(page, 'html.parser')
        goods = soup.find('div', class_='catalog-listing__items catalog-listing__items_divider-wide')
        list_of_goods = goods.find_all('div', attrs={"data-list-id": "main"}, recursive=False)
        result = []
        for good in list_of_goods:
            good_url = MAIN_URL + good.find('a')['href']
            result.append(good_url)
        return result

    def parse_page(self, page):
        soup = BeautifulSoup(page, 'html.parser')
        goods = soup.find('div', class_='catalog-listing__items catalog-listing__items_divider-wide')
        if not goods:
            return
        list_of_goods = goods.find_all('div', attrs={"data-list-id": "main"}, recursive=False)
        category = soup.find('h1', attrs={'itemprop': 'name'}).text
        results = []
        for good in list_of_goods:
            good_id = good['id'] if good.has_attr('id') else ""
            buy = good.find('button', attrs={'class': 'catalog-buy-button__button btn xs'})
            presence = True if buy else False
            price_raw = good.find('div', class_='item-price')
            price = price_raw.text if price_raw else ''
            link = MAIN_URL + good.find('a')['href']
            title_raw = good.find('div', class_='item-title')
            title = title_raw.text if title_raw else ''

            results.append({
                'id': good_id,
                'category': category,
                'title': title,
                'link': link,
            })

        return results

    def write_csv(self, goods_list):
        with open('goods.csv', mode='w', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file, delimiter=';')
            writer.writerow(['id', 'category', 'title', 'link'])

            for good in goods_list:
                writer.writerow(good.values())
            print('csv файл записан')

    def get_page(self, url, from_web=True):
        if not from_web:
            with open('page.html', encoding='utf-8') as file:
                page = file.read()
            result = self.parse_page(page)
            self.write_csv(result)
        else:
            result = []
            print('начинаю парсинг')
            for page_number in range(1, 999999):
                self.driver.get(url + str(page_number))
                page = self.driver.page_source
                try:
                    parsed_page = self.parse_page(page)
                except Exception as ex:
                    continue

                if not parsed_page:
                    print(f'закончен парсинг {page_number} страницы')
                    break

                result.extend(parsed_page)
                print(f'закончен парсинг {page_number} страницы')

            print('парсинг завершен')
            self.write_csv(result)

    def close_all(self):
        # close all open tabs
        if len(self.driver.window_handles) < 1:
            return
        for window_handle in self.driver.window_handles[:]:
            self.driver.switch_to.window(window_handle)
            self.driver.close()

    def quit(self):
        self.save_cookies()
        self.close_all()


if __name__ == "__main__":
    sel = SeleniumClass()
    sel.get_page(url)
    sel.quit()

