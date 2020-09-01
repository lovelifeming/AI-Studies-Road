# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from twisted.enterprise import adbapi


class SteelInformationPipeline:
    @classmethod
    def from_crawler(self, crawler):
        # 从项目的配置文件中读取相应的参数
        self.MYSQL_DB_NAME = crawler.settings.get("MYSQL_DB_NAME", 'test_db')
        self.HOST = crawler.settings.get("MYSQL_HOST", 'localhost')
        self.PORT = crawler.settings.get("MYSQL_PORT", 3306)
        self.USER = crawler.settings.get("MYSQL_USER", 'root')
        self.PASSWD = crawler.settings.get("MYSQL_PASSWORD", '123456')
        return self()

    def open_spider(self, spider):
        self.dbpool = adbapi.ConnectionPool('pymysql', host=self.HOST, port=self.PORT, user=self.USER,
                                            passwd=self.PASSWD, db=self.MYSQL_DB_NAME, charset='utf8')

    def close_spider(self, spider):
        self.dbpool.close()

    def process_item(self, item, spider):
        self.dbpool.runInteraction(self.insert_db, item)
        return item

    def insert_db(self, tx, item):
        values = (
            item['news_id'],
            item['title_name'],
            item['notes'],
            item['texts'],
            item['publish_time'],
            item['website_url'],
            item['website_name']
        )
        sql = 'INSERT INTO `p_ifm_announce_bigdata` (`news_id`, `title_name`, `notes`, `texts`, `create_time`,' \
              '`publish_time`,  `website`, `website_name`) VALUES (%s,%s,%s,%s,NOW(),%s,%s,%s) ' \
              'ON DUPLICATE KEY UPDATE modify_time= CURRENT_TIMESTAMP();'
        tx.execute(sql, values)
