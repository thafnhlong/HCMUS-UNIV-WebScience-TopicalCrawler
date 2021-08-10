import os

env = "development" # "production"

if env == "production":
    database_storage = os.path.dirname(__file__)+"/../database/data.db"

else:
    database_storage = ":memory:"