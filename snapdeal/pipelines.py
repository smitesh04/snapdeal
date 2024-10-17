# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from snapdeal.items import SnapdealItem
from snapdeal.db_config import  DbConfig
obj = DbConfig()


class SnapdealPipeline:
    def process_item(self, item, spider):
        if isinstance(item, SnapdealItem):
            obj.insert_data(item)

        return item
