
from datetime import datetime, timezone

from bson import ObjectId
from utility import (MongoDBSerializer,
                     Status,
                     DAL,
                     Logger)

LOGGER = Logger('PRODUCT_BUSINESS')


class MenuBusiness:
    def __init__(self) -> None:
        self.dal = DAL('menu_mapping')
        self.serializer = MongoDBSerializer()
        
    def __get_menu_items(self):
        menu_items = []
        try:
            db_result = self.dal.find_documents(collection='menu_items')
            menu_items = db_result.get('data')
        except Exception as e:
            LOGGER.error(e)
        
        return menu_items

    def __get_sections(self):
        sections = []
        try:
            db_result = self.dal.find_documents(collection='sections')
            sections = db_result.get('data')
        except Exception as e:
            LOGGER.error(e)
        
        return sections

    def __get_menu_mappings(self):
        mappings = []
        try:
            fields = {'id', 'menu_id', 'section_id', 'section_ordinal', 'menu_item_id', 'menu_item_ordinal', }
            db_result = self.dal.find_documents(collection='menu_mapping', fields=fields)
            mappings = db_result.get('data')
        except Exception as e:
            LOGGER.error(e)
        
        return mappings
    
    @staticmethod
    def __find_from_objects(items, key, value):
        for item in items:
            if item.get(key) == value:
                return item

    def get_menu_details(self, menu_id: str):
        result = {'status': Status.UNKNOWN, 'data': None}
        try:
            
            menu_details = self.dal.find_doc_by_id(menu_id, collection='menus')
            menu_details['sections'] = []
            mappings = self.__get_menu_mappings()
            sections = self.__get_sections()
            menu_items = self.__get_menu_items()
            
            for mapping in mappings:
                section_id = mapping.get('section_id')
                section_details = {}
                section_details['menu_items'] = []
                
                menu_item_id = mapping.get('menu_item_id')
                menu_item_details = self.__find_from_objects(menu_items, '_id', menu_item_id)
                
                existing_sections = menu_details.get('sections')
                if existing_section_details := self.__find_from_objects(existing_sections, '_id', section_id):
                    existing_section_details.get('menu_items').append(menu_item_details)
                else:
                    section_details = self.__find_from_objects(sections, '_id', section_id)
                    section_details['menu_items'] = [menu_item_details]
                    menu_details.get('sections').append(section_details)
                
            result['data'] = self.serializer.serialize(menu_details)
            
        except Exception as e:
            result['status'] = Status.ERROR
            LOGGER.error(e)
        else:
            result['status'] = Status.SUCCESS

        return result
