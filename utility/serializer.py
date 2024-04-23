from datetime import datetime
from bson.json_util import dumps
from bson import ObjectId
from datetime import datetime, date
from utility.constant import DateStringFormat
from pymongo.command_cursor import CommandCursor
import json


class MongoDBSerializer:
    def __init__(self) -> None:
        pass

    def serialize(self, data, **kwargs):
        if isinstance(data, CommandCursor):
            data = list(data)
            return self.__list_serialize(data, **kwargs)
        if isinstance(data, list):
            return self.__list_serialize(data, **kwargs)
        if isinstance(data, dict):
            return self.__dict_serialize(data, **kwargs)
        else:
            return data

    def __list_serialize(self, items: list, **kwargs):
        for i, item in enumerate(items):
            if isinstance(item, dict):
                items[i] = self.__dict_serialize(item, **kwargs)
            else:
                items[i] = item

        return items

    def __dict_serialize(self, item: dict, **kwargs):
        for key, value in item.items():
            if isinstance(value, ObjectId):
                item[key] = str(value)
            if isinstance(value, (date, datetime)):
                item[key] = value.strftime(DateStringFormat.ISO_FORMAT)
            if isinstance(value, list):
                if fields_keep_one_record := kwargs.get('fields_keep_one_record'):
                    if key in fields_keep_one_record:
                        value = value[0]
                        item[key] = self.serialize(value, **kwargs)
                        continue

                item[key] = self.__list_serialize(value, **kwargs)
            if isinstance(value, dict):
                item[key] = self.__dict_serialize(value, **kwargs)

        return item