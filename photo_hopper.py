import os
import requests

import facebook
import gdata.photos.service
import gdata.media

storage_location = "/tmp/photo_hopper.jpg"

def initialize():
    print("Hello, let's get started!\n")
    email = raw_input("What is your email address? ").strip().lower()
    albums = raw_input("\nPlease enter a comma separated, case sensitive list\n" +
    "of the names of the albums you would like to transfer: ")
    albums = [album_name.strip() for album_name in albums.split(",")]
    return email, albums


def authorize_facebook_client():
    print("\nNote: Valid Facebook API tokens can be obtained by going to\n" +
          "developers.facebook.com/tools/explorer. Make sure the token\n" +
          "you generate includes the user_photos permission.\n")
    access_token = raw_input("Enter a valid Facebook API token here: ")
    return facebook.GraphAPI(access_token)

def authorize_google_client(email):
    print("\nNote: Valid Google API tokens can be obtained by going to\n" +
          "developers.google.com/oauthplayground/. Make sure the token\n" +
          "you generate has the scope https://picasaweb.google.com/data/,\n" +
          "or choose Picasa Web v2 from the list.\n")
    access_token = raw_input("Enter a valid Google API token here: ")
    return gdata.photos.service.PhotosService(email=email,
                                              additional_headers=
                                              { 'Authorization' : 'Bearer %s' %
                                                access_token })
    
def get_fb_album(fb_client, album_name):
    user = fb_client.get_object(id="me")
    user_albums = fb_client.get_connections(user["id"], "albums")["data"]
    album_names = [album["name"] for album in user_albums]
    return user_albums[album_names.index(album_name)]


def get_fb_album_photos(fb_client, album):
    album_page = fb_client.get_connections(album["id"], "photos")
    album_photos = album_page["data"]
    while True:
        try:
            # Attempt to get the next page of photos
            album_page = requests.get(album_page["paging"]["next"]).json()
            for photo in album_page["data"]:
                album_photos.append(photo)
        except KeyError:
            # There are no more pages (fb_album_page["paging"]["next"] throws KeyError)
            break
    return album_photos
    
def create_gphotos_album(gd_client, album):
    try:
        album_summary = album["description"]
    except KeyError:
        album_summary = "Hopped from Facebook to Google Photos using Photo Hopper"
    gphoto_album = gd_client.InsertAlbum(title=album["name"], summary=album_summary)
    print("\nNew Google Photos album '%s' initialized\n" % album["name"])
    return '/data/feed/api/user/%s/albumid/%s' % ('default', gphoto_album.gphoto_id.text)

def hop_photos(gd_client, photos, url, storage_location):
    for i in range(len(photos)):
        photo = photos[i]
        print("Hopping photo %s of %s" % (i + 1, len(photos)))
        try:
            photo_caption = photo["name"]
        except KeyError:
            photo_caption = "Doing the thing."
        open(storage_location, 'wb').write(requests.get(photo["images"][0]["source"]).content)
        gd_client.InsertPhotoSimple(url, photo["id"], photo_caption,
                                    storage_location, content_type='image/jpeg')
    os.remove(storage_location)

def main():
    email, albums = initialize()
    fb_client = authorize_facebook_client()
    gd_client = authorize_google_client(email)
    for album in albums:
        fb_album = get_fb_album(fb_client, album)
        fb_photos = get_fb_album_photos(fb_client, fb_album)
        gphoto_url = create_gphotos_album(gd_client, fb_album)
        print("Starting hop of '%s'" % album)
        hop_photos(gd_client, fb_photos, gphoto_url, storage_location)
        print("Finished hopping '%s'" % album)
    print("\nAll done!")

if __name__ == "__main__":
    main()
