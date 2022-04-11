# Importing required modules
#%%
from pymongo import MongoClient
from pandas import DataFrame
  
   
# Connecting to MongoDB server
# client = MongoClient('host_name',
# 'port_number')

#%%
client = MongoClient('localhost', 27017)
  
#%%
db=client["pasanti_test"]
#%%
data= db.signals.find()
data[1]
# Now creating a Cursor instance
# using find() function
#%%


list_cur = list(data)
  
# Converting to the DataFrame
df = DataFrame(list_cur)
df