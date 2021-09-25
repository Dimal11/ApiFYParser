import requests
from bs4 import BeautifulSoup
import time
import json
import pandas as pd
import d6tstack.utils
from config import Config
import psycopg2
from psycopg2 import Error



class Parser:
    CURRENT_TIME = int(time.time())
    URL = 'https://finance.yahoo.com'
    HEADERS = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36',
        'accept': '*/*'}

    def get_information_url(self, company):
        """ Данная ссылка на JSON была найдена на просторах интернета для получения
           даты с которой начнется период получения данных"""
        URL_INFORMATION_OF_COMPANY = f'https://query1.finance.yahoo.com/v8/finance/chart/' \
                                     f'{company}?symbol={company}' \
                                     f'&period1=0&period2=9999999999&' \
                                     f'interval=1d&' \
                                     f'includePrePost=true&' \
                                     f'events=div%2Csplit'
        return URL_INFORMATION_OF_COMPANY

    def get_html(self, url, params=None):
        r = requests.get(url, headers=self.HEADERS, params=params)
        return r

    # Данный код оставляю для ознакомления

    # def get_search_url(html):
    #     soup = BeautifulSoup(html, 'html.parser')
    #     item = soup.find('form', class_='D(tb) H(35px) Pos(r) Va(m) W(100%) finsrch-enable-perf').get('action')
    #     search_url = URL + str(item)
    #     return search_url

    # def get_history_url(url, company):
    #     company_url = url + company
    #     html = get_html(company_url)
    #     soup = BeautifulSoup(html.text, 'html.parser')
    #     items = soup.find_all("a",
    #                           class_='Lh(44px) Ta(c) Bdbw(3px) Bdbs(s) Px(12px) C($linkColor) Bdbc($seperatorColor)
    #                           D(b) Td(n) selected_Bdbc($linkColor) selected_C($primaryColor) selected_Fw(b)')
    #     for item in items:
    #         tab = item.find('span').get_text()
    #         if tab == 'Historical Data':
    #             url = item.get('href')
    #             break
    #         else:
    #             continue
    #     history_url = URL + str(url)
    #     return history_url

    def get_period_1(self, url):
        json_file = self.get_html(url)
        with open('INFO_COMPANY.json', "w") as f:
            f.write(json_file.text)
        with open('INFO_COMPANY.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        period_1 = data["chart"]["result"][0]["meta"]["firstTradeDate"]

        return period_1

    """ Как определить максимальный период запрашиваемых данных на вкладке 'Historical Data' я не знаю. 
    По этому для успешной реализации приложения я скопировал путь к ссылке
    'Download' и с помощью меток времени установил корректный макс промежуток"""

    def get_download_url(self,
                         period_2=CURRENT_TIME, interval='1d',
                         filter='history',
                         frequency='1d',
                         include_Adjusted_Close=True,
                         url_info_company=None,
                         company=None):
        period_1 = self.get_period_1(url_info_company)
        url_download = f'https://query1.finance.yahoo.com/v7/finance/download/' \
                       f'{company}?' \
                       f'period1={period_1}' \
                       f'&period2={period_2}' \
                       f'&interval={interval}' \
                       f'&filter={filter}' \
                       f'&frequency={frequency}' \
                       f'&includeAdjustedClose={include_Adjusted_Close}'
        return url_download

    def csv_to_database(self, url, name_of_company):
        data_df = pd.read_csv(url)
        d6tstack.utils.pd_to_psql(data_df, Config.SQLALCHEMY_DATABASE_URI, f'{name_of_company}', if_exists='replace')

    def get_json_from_db(self, company):
        data_list = []
        try:
            connection = psycopg2.connect(user='postgres',
                                          password='dl110987DL',
                                          host='localhost',
                                          port='5432',
                                          database='parser')
            cursor = connection.cursor()
            postgreSQL_select_Query = f"select * from {company.lower()}"
            cursor.execute(postgreSQL_select_Query)
            data = cursor.fetchall()
            for row in data:
                date = {row[0]: {'Open': row[1],
                                 'High': row[2],
                                 'Low': row[3],
                                 'Close': row[4],
                                 'Adj Close': row[5],
                                 'Volume': row[6]}}
                data_list.append(date)
        except (Exception, Error) as error:
            print('Ошибка', error)
        finally:
            if connection:
                cursor.close()
                connection.close()

        return data_list

    def parse(self, company):
        url_information_of_company = self.get_information_url(company)
        html = self.get_html(self.URL)
        if html.status_code == 200:
            url = self.get_download_url(url_info_company=url_information_of_company, company=company)
            self.csv_to_database(url=url, name_of_company=company)
            json_file = self.get_json_from_db(company)
        else:
            print('Error')
        return json_file

