import pymongo


def create_dict(**kwargs):
    return kwargs


class db_utils:
    def __init__(self, collection, **template):
        self.collection = collection
        self.template = template

    def initialize(self):
        return utils(self.collection)

    def initialize_template(self):
        return utils(self.collection, self.template)

    @classmethod
    def create_dict(cls, **kwargs):
        return kwargs


class utils:
    def __init__(self, collection: pymongo.collection.Collection, template=None):
        if template is None:
            template = {}
        self.db_dict = {}
        self.collection = collection
        self.template = template

    def initialize_dict(self):
        """Initialize/reset dictionary for the object"""
        self.db_dict = {}
        return self

    def add(self, **kwargs):
        """Add to dictionary"""
        self.db_dict.update(kwargs)
        return self

    def add_operators(self, **kwargs):
        """Add operators to dictionary (start with a $)"""
        self.db_dict.update({f"${key}": kwargs[key] for key in kwargs})
        return self

    def insert_one(self):
        """Insert dictionary into database"""
        self.collection.insert_one(self.db_dict)

    def update_one(self, update_filter, upsert: bool = False):
        """Update database with given filter and if upsert is needed"""
        self.collection.update_one(update_filter, self.db_dict, upsert=upsert)

    def upsert_from_template(self, update_filter, **template_extras):
        self.add_operators(setOnInsert={key: self.template[key] for key in self.template if key not in template_extras})
        self.collection.update_one(update_filter, self.db_dict, upsert=True)

    def insert_from_template(self, **kwargs):
        self.add(**kwargs, **self.template)
        self.insert_one()

