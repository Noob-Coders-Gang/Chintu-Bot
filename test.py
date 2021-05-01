import pickle
from cogs.data_classes.warning import Warn
from datetime import datetime

obj = Warn(3,"test",datetime.now())
print(Warn.pickle_warn(obj))