from pymongo import MongoClient


try:
    # Python 3.x
    from urllib.parse import quote_plus
except ImportError:
    # Python 2.x
    from urllib import quote_plus

# uri = "mongodb://%s:%s@%s" % (
#     quote_plus("thangld_1202_user"), quote_plus("QAZwsx*098#pl,"), "35.184.69.50:27017")
# client = MongoClient(uri)

uri = "mongodb://%s:%s@%s" % (
    quote_plus("thangld_1202_user"), quote_plus("QAZwsx*098#pl,"), "35.184.69.50:27017")
client = MongoClient(uri)

client = MongoClient("35.184.69.50",27017)
db = client.test
data = db['account'].find({})
for item in data:
    print item


