""" Configuration file for the application,
credentials are hardcoded as this is a demonstration project """

import os

DB_HOST = os.getenv("DB_HOST", "couchbase://localhost")
DB_USER = "administrator"
DB_PASSWORD = "administrator"
DB_BUCKET = "foursquare"
DB_SCOPE = "_default"
DB_BUCKET_RAM_QUOTA_MB = 1024
USER_COLLECTION = "users"
VENUE_COLLECTION = "venues"
CHECKIN_COLLECTION = "checkins"
CHECKINS_FILE = "dataset_WWW_Checkins_anonymized.txt"
VENUES_FILE = "raw_POIs.txt"
FRIENDSHIPS_FILES = ["dataset_WWW_friendship_old.txt", "dataset_WWW_friendship_new.txt"]
