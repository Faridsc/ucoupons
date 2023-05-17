import sqlite3
from scrapy.exceptions import DropItem


class UcouponsPipeline:
    def __init__(self) -> None:
        self.conn: sqlite3.Connection
        self.__DB_NAME = "./db/coupons.db"

    def create_table(self, conn):
        SCHEMA = """
                CREATE TABLE IF NOT EXISTS coupons (
                id INTIGER AUTO INCREMENT UNIQUE PRIMARY KEY,
                title VARCHAR(255) UNIQUE NOT NULL,
                lang VARCHAR(60) NOT NULL,
                date VARCHAR(10),
                url VARCHAR(255) UNIQUE NOT NULL,
                img VARCHAR(255),
                description TEXT,
                price VARCHAR(20),
                topic VARCHAR(255)
                );
            """
        try:
            c = conn.cursor()
            c.execute(SCHEMA)
        except sqlite3.Error as e:
            raise e

    def add_item(self, conn, item):
        s = """
            INSERT INTO coupons (id, title, lang, date, url, img, description, price, topic)
            VALUES(NULL, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        try:
            c = conn.cursor()
            c.execute(s, list(item.values()))
            conn.commit()
        except:
            raise DropItem("item not added to the database")

    def open_spider(self, spider):
        try:
            self.conn = sqlite3.connect(self.__DB_NAME)
            self.create_table(self.conn)
        except sqlite3.Error as e:
            spider.logger.error(e)
            spider.logger.error(
                "CONNEXTION NOT EXTABLISHED WITH {} DATABASE".format(self.__DB_NAME)
            )

    def process_item(self, item, spider):
        self.add_item(self.conn, item)

    def close_spider(self, spider):
        if self.conn:
            self.conn.close()
