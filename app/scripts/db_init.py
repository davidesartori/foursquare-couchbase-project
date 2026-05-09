"""Script to initialize the Couchbase database with users, venues, and friendships data."""
import app.domain.models as models
from pathlib import Path
from datetime import datetime, timedelta
import random
import time
from couchbase.cluster import Cluster
from couchbase.auth import PasswordAuthenticator
from couchbase.options import ClusterOptions
from couchbase.management.buckets import CreateBucketSettings
from couchbase.management.collections import CollectionSpec
from couchbase.exceptions import BucketNotFoundException


def generate_random_birth_date():
    """Generate a random birth date between 60 years before 2012 and 7 years before 2012."""
    reference_date = datetime(2012, 1, 1)
    start = reference_date - timedelta(days=60 * 365)
    end = reference_date - timedelta(days=7 * 365)
    return (start + (end - start) * random.random()).date()


def generate_random_old_friendship_date():
    """Generate a random friendship date between 5 years before april 2012 and april 2012."""
    reference_date = datetime(2012, 4, 1)
    start = reference_date - timedelta(days=60 * 365)
    end = datetime(2012, 4, 1)
    return (start + (end - start) * random.random()).date()


def generate_random_new_friendship_date():
    """Generate a random friendship date between april 2012 and january 2014."""
    start = datetime(2012, 4, 1)
    end = datetime(2014, 1, 1)
    return (start + (end - start) * random.random()).date()


def insert_or_update_user(collection, user):
    """Insert a new user document or update an existing one.
    """

    checkins = []

    for checkin in user.checkins:
        checkins.append({
            "timestamp": checkin.timestamp.isoformat(),
            "offset": checkin.offset,
            "venueId": checkin.venueId,
            "utcTime": checkin.utcTime
        })

    collection.upsert(
        f"user::{user.id}",
        {
            "id": user.id,
            "name": "",
            "surname": "",
            "birthDate": str(user.birthDate),
            "country": user.country.model_dump(exclude_none=True),
            "checkins": checkins
        }
    )


def insert_or_update_venue(collection, venue):
    """Insert a new venue document or update an existing one.
    """
    collection.upsert(
        f"venue::{venue.id}",
        {
            "id": venue.id,
            "name": venue.name,
            "category": venue.category.model_dump(exclude_none=True),
            "latitude": venue.latitude,
            "longitude": venue.longitude,
            "country": venue.country.model_dump(exclude_none=True),
            "majorId": venue.majorId
        }
    )

def insert_or_update_friendship(collection, friendship):
    """Insert a new friendship document or update an existing one.
    """
    collection.upsert(
        f"friendship::{friendship.user1}::{friendship.user2}",
        {
            "user1": friendship.user1,
            "user2": friendship.user2,
            "status": friendship.status.value,
            "friendSince": friendship.friendSince.isoformat()
        }
    )


if __name__ == "__main__":
    USERS_COLLECTION = "users"
    VENUES_COLLECTION = "venues"
    FRIENDSHIPS_COLLECTION = "friendships"

    CHECKINS_FILE = "dataset_WWW_Checkins_anonymized.txt"
    VENUES_FILE = "raw_POIs.txt"
    FRIENDSHIPS_FILES = ["dataset_WWW_friendship_old.txt", "dataset_WWW_friendship_new.txt"]

    users = {}
    venues = {}
    friendships = []

    cluster = Cluster(
        "couchbase://localhost",
        ClusterOptions(
            PasswordAuthenticator("administrator", "administrator")
        )
    )

    cluster.wait_until_ready(timedelta(seconds=5))

    try:
        bucket = cluster.bucket("foursquare")
    except BucketNotFoundException as e:
        bucket_manager = cluster.buckets()

        bucket_manager.create_bucket(
            CreateBucketSettings(
                name="foursquare",
                bucket_type="couchbase",
                ram_quota_mb=1024
            )
        )

        time.sleep(5)

        bucket = cluster.bucket("foursquare")

    collection_manager = bucket.collections()
    existing_collections = [c.name for scope in collection_manager.get_all_scopes()
                            for c in scope.collections]

    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"

    print("Processing check-ins...")
    with open(DATA_DIR / CHECKINS_FILE, encoding="utf-8") as checkins_in:
        for i, checkin_line in enumerate(checkins_in):
            checkin = checkin_line.strip().split("\t")
            user_id = int(checkin[0])

            try:
                timestamp = datetime.strptime(
                    checkin[2], "%a %b %d %H:%M:%S %z %Y")
            except ValueError:
                print(
                    f"Error parsing timestamp for checkin: {checkin_line}")
                continue

            offset = int(checkin[3])
            venue_id = checkin[1]

            utc_time = checkin[2]

            if str(user_id) in users:
                user_instance = users[str(user_id)]
                user_instance.checkins.append(models.Checkin(
                    timestamp=timestamp, offset=offset, venueId=venue_id, utcTime=utc_time))
            else:
                checkin_instance = models.Checkin(
                    timestamp=timestamp, offset=offset, venueId=venue_id, utcTime=utc_time)
                user_instance = models.User(id=user_id, name="", surname="",
                                            birthDate=generate_random_birth_date(),
                                            country=models.Country(code="US",
                                                                name="United States of America"),
                                            checkins=[checkin_instance])

                users[str(user_id)] = user_instance

            if venue_id not in venues:
                venues[venue_id] = None

        print("Check-in processing complete")

    print("Processing venues...")
    with open(DATA_DIR / VENUES_FILE, encoding="utf-8") as venues_in:
        for i, venue_line in enumerate(venues_in):
            venue = venue_line.strip().split("\t")
            venue_name = venue[0]
            latitude = float(venue[1])
            longitude = float(venue[2])
            category = venue[3]
            country = venue[4]

            venue_instance = models.Venue(
                id=venue_name,
                name=venue_name,
                category=models.VenueCategory(id="".join(category.lower().split(' ')),
                                              name=category),
                latitude=latitude,
                longitude=longitude,
                country=models.Country(code=country, name=country),
                majorId=0)

            if venue_name in venues:
                venues[venue_name] = venue_instance

    print("Venue processing complete")

    print("Processing friendships...")
    for friendship_file in FRIENDSHIPS_FILES:
        with open(DATA_DIR / friendship_file, encoding="utf-8") as friendships_in:
            for i, friendship_line in enumerate(friendships_in):
                friendship = friendship_line.strip().split("\t")
                user1 = int(friendship[0])
                user2 = int(friendship[1])
                status = models.FriendshipStatus("accepted")
                friend_since = datetime.now()

                friendships.append(models.Friendship(
                    user1=user1,
                    user2=user2,
                    status=status,
                    friendSince=friend_since
                ))

    print("Friendship processing complete")

    print("Inserting users into Couchbase...")

    if USERS_COLLECTION not in existing_collections:
        collection_manager.create_collection(
            CollectionSpec(USERS_COLLECTION, scope_name="_default"))
        time.sleep(1)

    users_collection = bucket.collection(USERS_COLLECTION)

    for user in users.values():
        if user is not None:
            insert_or_update_user(users_collection, user)

    print("Done!")

    print("Inserting venues into Couchbase...")

    if VENUES_COLLECTION not in existing_collections:
        collection_manager.create_collection(CollectionSpec(VENUES_COLLECTION,
                                                            scope_name="_default"))
        time.sleep(1)

    venues_collection = bucket.collection(VENUES_COLLECTION)

    for venue in venues.values():
        if venue is not None:
            insert_or_update_venue(venues_collection, venue)

    print("Done!")

    print("Inserting friendships into Couchbase...")

    if FRIENDSHIPS_COLLECTION not in existing_collections:
        collection_manager.create_collection(
            CollectionSpec(FRIENDSHIPS_COLLECTION, scope_name="_default"))
        time.sleep(1)

    friendships_collection = bucket.collection(FRIENDSHIPS_COLLECTION)

    for friendship in friendships:
        insert_or_update_friendship(friendships_collection, friendship)

    print("Done!")
