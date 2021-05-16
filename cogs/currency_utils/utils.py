import pymongo
from datetime import datetime


class currency_utils:
    def __init__(self, collection: pymongo.collection.Collection):
        self.collection = collection

    def update_and_insert(self, doc_id: int, inc_vals=None, set_vals=None, wallet=True, bank=True, bank_limit=True,
                          inventory=True, t_daily=True, t_weekly=True, t_monthly=True, commands=True):
        bool_dict = {
            "wallet": wallet,
            "bank": bank,
            "bank_limit": bank_limit,
            "commands": commands,
            "t_daily": t_daily,
            "t_weekly": t_weekly,
            "t_monthly": t_monthly
        }
        set_on_insert_dict = {}
        update_dict = {}
        if inc_vals:
            update_dict["$inc"] = inc_vals
        if set_vals:
            update_dict["$set"] = set_vals
        if inventory:
            set_on_insert_dict["inventory"] = {}
        for key in bool_dict:
            if bool_dict[key]:
                set_on_insert_dict[key] = 0

        update_dict["$setOnInsert"] = set_on_insert_dict
        self.collection.update_one({"_id": doc_id}, update_dict, upsert=True)

    def update(self, doc_id: int, inc_vals=None, set_vals=None):
        update_dict = {}
        if inc_vals:
            update_dict["$inc"] = inc_vals
        if set_vals:
            update_dict["$set"] = set_vals
        self.collection.update_one({"_id": doc_id}, update_dict)

    def insert_new_document(self,
                            doc_id: int,
                            wallet: int = 0,
                            bank: int = 0,
                            bank_limit: int = 0,
                            commands: int = 0,
                            inventory=None,
                            t_daily: datetime = 0,
                            t_weekly: datetime = 0,
                            t_monthly: datetime = 0):
        if inventory is None:
            inventory = {}
        self.collection.insert_one({
            "_id": doc_id,
            "wallet": wallet,
            "bank": bank,
            "bank_limit": bank_limit,
            "commands": commands,
            "inventory": inventory,
            "t_daily": t_daily,
            "t_weekly": t_weekly,
            "t_monthly": t_monthly
        })

    def get_balance(self, user_id: int):
        coins = self.collection.find_one({"_id": user_id}, {"wallet": 1, "bank": 1})
        try:
            return coins['wallet'], coins['bank']
        except TypeError:
            self.insert_new_document(user_id)
            return 0, 0