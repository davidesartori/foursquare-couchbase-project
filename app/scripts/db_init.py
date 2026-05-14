"""Script to initialize the Couchbase database with users, venues, and friendships data."""
import app.domain.models as models
import app.config as config
from app.repositories.user_repository import UserRepository
from app.repositories.venue_repository import VenueRepository
from app.repositories.checkin_repository import CheckinRepository
from app.services.db_service import CouchbaseService
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


def process_checkins(path, checkins_dict, user_dict, venue_dict):
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

            if venue_id in venue_dict:
                venue_instance = venue_dict[venue_id]
            else:
                venue_instance = models.Venue(id="", name="Unknown Venue",
                                              category=models.VenueCategory(id="unknown",
                                                                            name="Unknown"),
                                              location=models.Location.get_coordinates_list(
                                                  0.0, 0.0),
                                              country=models.Country(code="XX", name="Unknown"))

            checkin_instance = models.Checkin(
                id=i, userId=user_id, venue=venue_instance, utcTimestamp=timestamp, offset=offset)

            checkins_dict[i] = checkin_instance

            if str(user_id) not in user_dict:
                user_instance = models.User(id=user_id, name="", surname="",
                                            birthDate=generate_random_birth_date(),
                                            country=models.Country(code="US",
                                                                   name="United States of America"),
                                                                   friends=[])

                user_dict[str(user_id)] = user_instance


def process_venues(path, venue_dict):
    """ Process venues from the file specified in the configuration and populate the venue_dict. """
    with open(path / config.VENUES_FILE, encoding="utf-8") as venues_in:
        for _, venue_line in enumerate(venues_in):
            venue = venue_line.strip().split("\t")
            venue_name = venue[0]
            latitude = float(venue[1])
            longitude = float(venue[2])
            category = venue[3]
            country = venue[4]

            venue_instance = models.Venue(
                id=venue_name,
                name=venue_name,
                location=models.Location.get_coordinates_list(
                    latitude, longitude),
                category=models.VenueCategory(id="".join(category.lower().split(' ')),
                                              name=category),
                country=models.Country(code=country, name=country))

            venue_dict[venue_name] = venue_instance


def process_friendships_from_files(path, user_dict):
    """ Process friendships from the files specified in the configuration and 
    append them to the friendships list. """
    for friendship_file in config.FRIENDSHIPS_FILES:
        with open(path / friendship_file, encoding="utf-8") as friendships_in:
            for i, friendship_line in enumerate(friendships_in):
                friendship = friendship_line.strip().split("\t")
                user1 = int(friendship[0])
                user2 = int(friendship[1])
                status = models.FriendshipStatus("accepted")
                friend_since = generate_random_old_friendship_date(
                ) if i == 0 else generate_random_new_friendship_date()

                if str(user1) in user_dict and str(user2) in user_dict:
                    friendship_instance = models.Friendship(
                        friendId=user2, status=status, friendSince=friend_since)
                    user_dict[str(user1)].friends.append(friendship_instance)

                    friendship_instance = models.Friendship(
                        friendId=user1, status=status, friendSince=friend_since)
                    user_dict[str(user2)].friends.append(friendship_instance)


def main():
    """ Main function to initialize the Couchbase database with users, venues,
    and friendships data."""
    db_service = CouchbaseService()
    user_repository = UserRepository(db_service)
    venue_repository = VenueRepository(db_service)
    checkin_repository = CheckinRepository(db_service)

    users = {}
    venues = {}
    checkins = {}

    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"

    print("Processing venues...")
    process_venues(DATA_DIR, venues)
    print("Venue processing complete")

    print("Processing check-ins...")
    process_checkins(DATA_DIR, checkins, users, venues)
    print("Check-in processing complete")

    print("Processing friendships...")
    process_friendships_from_files(DATA_DIR, users)
    print("Friendship processing complete")

    print("Inserting users into Couchbase...")

    for user in users.values():
        if user is not None:
            user_repository.upsert(user)

    print("Done!")

    print("Inserting venues into Couchbase...")

    for venue in venues.values():
        venue_repository.upsert(venue)

    print("Done!")

    print("Inserting check-ins into Couchbase...")

    for checkin in checkins.values():
        checkin_repository.upsert(checkin)

    print("Done!")

    db_service.close()


if __name__ == "__main__":
    main()
