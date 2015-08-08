#import os
#import requests
#
#import facebook
#import gdata.photos.service
#import gdata.media
from hoppers import *

storage_location = "/tmp/photo_hopper.jpg"

def create_hopper(email, album_names):
    service = raw_input("\nAre the photos you'd like to hop today stored on Facebook or Google? ").strip().lower()
    if service == "facebook":
        hopper = FacebookHopper(email, album_names)
    elif service == "google":
        hopper = GoogleHopper(email, album_names)
    else:
        print("\nSorry, uncrecognized service, try entering it again.")
        hopper = create_hopper(email, album_names)
    return hopper

def initialize():
    print("Hello, let's get started!\n")
    email = raw_input("What is the  email address you use for Google Photos? ").strip().lower()
    albums = raw_input("\nPlease enter a comma separated, case sensitive list\n" +
    "of the names of the albums you would like to transfer: ")
    album_names = [album_name.strip() for album_name in albums.split(",")]
    return create_hopper(email, album_names)

def main():
    hopper = initialize()
    hopper.authorize_facebook_client()
    hopper.authorize_google_client()
    for album_name in hopper.album_names:
        album = hopper.find_album(album_name)
        photos = hopper.list_album_photos(album)
        upload_url = hopper.create_album(album)
        print("Starting hop of '%s'" % album_name)
        hopper.hop(photos, upload_url)
        print("Finished hopping '%s'" % album_name)
    print("\nAll done!")

if __name__ == "__main__":
    main()
