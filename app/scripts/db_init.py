"""Script to initialize the Couchbase database with users, venues, and friendships data."""
import app.domain.models as models
import app.config as config
from app.repositories.user_repository import UserRepository
from app.repositories.venue_repository import VenueRepository
from app.repositories.friendship_repository import FriendshipRepository
from pathlib import Path
from datetime import datetime, timedelta
import random

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


def process_checkins(path, user_dict, venue_dict):
    """ Process check-ins from the file specified in the configuration and
    populate the user_dict and venue_dict. """
    with open(path / config.CHECKINS_FILE, encoding="utf-8") as checkins_in:
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

            if str(user_id) in user_dict:
                user_instance = user_dict[str(user_id)]
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

                user_dict[str(user_id)] = user_instance

            if venue_id not in venue_dict:
                venue_dict[venue_id] = None


def process_venues(path, venue_dict):
    """ Process venues from the file specified in the configuration and populate the venue_dict. """
    with open(path / config.VENUES_FILE, encoding="utf-8") as venues_in:
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

            if venue_name in venue_dict:
                venue_dict[venue_name] = venue_instance


def process_friendships_from_files(path, friendships):
    """ Process friendships from the files specified in the configuration and 
    append them to the friendships list. """
    for friendship_file in config.FRIENDSHIPS_FILES:
        with open(path / friendship_file, encoding="utf-8") as friendships_in:
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


def main():
    """ Main function to initialize the Couchbase database with users, venues,
    and friendships data."""
    user_repository = UserRepository()
    venue_repository = VenueRepository()
    friendship_repository = FriendshipRepository()

    users = {}
    venues = {}
    friendships = []

    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"

    print("Processing check-ins...")
    process_checkins(DATA_DIR, users, venues)
    print("Check-in processing complete")

    print("Processing venues...")
    process_venues(DATA_DIR, venues)

    print("Venue processing complete")

    print("Processing friendships...")
    process_friendships_from_files(DATA_DIR, friendships)
    print("Friendship processing complete")

    print("Inserting users into Couchbase...")

    for user in users.values():
        if user is not None:
            user_repository.upsert(user)

    print("Done!")

    print("Inserting venues into Couchbase...")

    for venue in venues.values():
        if venue is not None:
            venue_repository.upsert(venue)

    print("Done!")

    print("Inserting friendships into Couchbase...")

    for friendship in friendships:
        friendship_repository.upsert(friendship)

    print("Done!")


if __name__ == "__main__":
    main()
