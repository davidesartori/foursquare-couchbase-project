import app.domain.models as models
from pathlib import Path
from datetime import datetime, timedelta
import random, time
from couchbase.cluster import Cluster
from couchbase.auth import PasswordAuthenticator
from couchbase.options import ClusterOptions
import couchbase.subdocument as SD
from couchbase.management.buckets import CreateBucketSettings
from couchbase.management.collections import CollectionSpec
from couchbase.exceptions import DocumentNotFoundException, BucketNotFoundException


def generate_random_birth_date():
    """Generate a random birth date between 60 years before 2012 and 7 years before 2012."""
    reference_date = datetime(2012, 1, 1)
    start = reference_date - timedelta(days=60 * 365)
    end = reference_date - timedelta(days=7 * 365)
    return (start + (end - start) * random.random()).date()


def insert_or_update_user(collection, user):
    """Insert a new user document or update an existing one with a new check-in.

    If the user document exists, append the new checkin to the existing
    checkins array. If the user document does not exist, create it with the
    provided user data and the initial checkin.
    """
    user_checkin = user.checkins[0]
    checkin_doc = {
        "timestamp": user_checkin.timestamp.isoformat() 
        if hasattr(user_checkin.timestamp, "isoformat")
        else user_checkin.timestamp,
        "offset": user_checkin.offset,
        "venueId": user_checkin.venueId
    }

    try:
        collection.mutate_in(
            f"user::{user.id}",
            [
                SD.array_append("checkins", checkin_doc)
            ]
        )
    except DocumentNotFoundException:
        collection.upsert(
            f"user::{user.id}",
            {
                "id": user.id,
                "name": "",
                "surname": "",
                "birthDate": str(user.birthDate),
                "country": user.country.model_dump(),
                "checkins": [checkin_doc]
            }
        )


if __name__ == "__main__":
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
    existing = [c.name for scope in collection_manager.get_all_scopes()
                for c in scope.collections]

    if "users" not in existing:
        collection_manager.create_collection(CollectionSpec("users", scope_name="_default"))
        time.sleep(1)

    users_collection = bucket.collection("users")

    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"

    # creating processed data directory
    Path(DATA_DIR / "processed").mkdir(parents=True, exist_ok=True)
    PROCESSED_DATA_DIR = DATA_DIR / "processed"

    with open(DATA_DIR / "dataset_WWW_Checkins_anonymized.txt", encoding="utf-8") as checkins_in:
        for i, checkin_line in enumerate(checkins_in):
            checkin = checkin_line.strip().split("\t")
            user_id = int(checkin[0])

            try:
                timestamp = datetime.strptime(
                    checkin[2], "%a %b %d %H:%M:%S %z %Y")
            except ValueError:
                print(f"Error parsing timestamp for checkin: {checkin_line}")
                continue

            offset = int(checkin[3])
            venueId = checkin[1]

            checkin_instance = models.Checkin(
                timestamp=timestamp, offset=offset, venueId=venueId)
            user_instance = models.User(id=user_id, name="", surname="",
                                        birthDate=generate_random_birth_date(),
                                        country=models.Country(code="US",
                                                               name="United States of America"),
                                        checkins=[checkin_instance])

            insert_or_update_user(users_collection, user_instance)

            if i % 100000 == 0 and i > 0:
                print(f"Processed {i} values")
