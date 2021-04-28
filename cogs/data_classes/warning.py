import discord
from datetime import datetime

class Warn:
    def __init__(self, 
    #warned_member:discord.Member, 
    moderator:discord.Member, 
    #guild:discord.Guild, 
    warning_message:discord.Message, 
    date_time=None, reason=None):
        #self.warned_member = warned_member
        self.moderator = moderator
        #self.guild = guild
        self.warning_message = warning_message
        if date_time is None:
            self.date_time = datetime.now()
        else:
            self.date_time = date_time
        if reason is None:
            self.reason = "No reason was provided"
        else:
            self.reason = reason
        