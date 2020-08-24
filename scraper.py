# -*- coding: UTF-8 -*-
import requests
from bs4 import BeautifulSoup
import pymysql


class Stock:

    def __init__(self, *stock_num):
        self.stock_num = stock_num
        print(self.stock_num)

    def scrape(self):
        result = []
        for stock_nums in self.stock_num:
            response = requests.get(
                "https://tw.stock.yahoo.com/q/q?s=" + stock_nums)
            soup = BeautifulSoup(response.text.replace("加到投資組合", ""), "lxml")

            stock_date = soup.find(
                "font", {"class": "tt"}).getText().strip()[-9:]  # collect data

            # collect the third table from html
            tables = soup.find_all("table")[2]
            # collect first ten data from the table just collected
            tds = tables.find_all("td")[0:11]

            result.append((stock_date,) + tuple(td.getText().strip()
                                                for td in tds))

        return result

    def save(self, stocks):

        db_settings = {
            "host": "127.0.0.1",
            "port": 3306,
            "user": "root",
            "password": "adminadmin",
            "db": "stock",
            "charset": "utf8"
        }

        try:
            conn = pymysql.connect(**db_settings)

            with conn.cursor() as cursor:
                sql = """INSERT INTO stock_data(
                            market_date,
                            stock_name,
                            market_time,
                            final_price,
                            buy_price,
                            sell_price,
                            ups_and_downs,
                            lot,
                            yesterday_price,
                            opening_price,
                            highest_price,
                            lowest_price)
                     VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

                for stock in stocks:
                    cursor.execute(sql, stock)
                conn.commit()

        except Exception as ex:
            print("Exception:", ex)

num = input("請輸入股票代碼：")
stock = Stock(num)
print(stock.scrape())
stock.save(stock.scrape())
