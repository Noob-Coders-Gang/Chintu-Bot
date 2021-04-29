import discord
from datetime import datetime
from dataclasses import dataclass
import pickle

@dataclass
class Warn:
    warn_id:int
    moderator_id:int
    warning_message_id:int
    reason:str
    date_time:datetime

    @classmethod
    def pickle_warn(self, obj):
        return pickle.dumps(obj)
    # def __init__(self, 
    # moderator:discord.Member, 
    # warning_message:discord.Message, 
    # date_time=None, reason=None):
    #     self.moderator = moderator
    #     self.warning_message = warning_message
    #     if date_time is None:
    #         self.date_time = datetime.now()
    #     else:
    #         self.date_time = date_time
    #     if reason is None:
    #         self.reason = "No reason was provided"
    #     else:
    #         self.reason = reason
    
    
        