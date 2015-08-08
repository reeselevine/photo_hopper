import os
import requests
import facebook
import gdata.photos.service
import gdata.media

class Hopper:

    storage_loc = "/tmp/photo_hopper.jpg"

    def __init__(self, email, album_names):
        self.email = email
        self.album_names = album_names
        
    def authorize_facebook_client(self):
        print("\nNote: Valid Facebook API tokens can be obtained by going to\n" +
              "developers.facebook.com/tools/explorer. Make sure the token\n" +
              "you generate includes the user_photos permission.\n")
        access_token = raw_input("Enter a valid Facebook API token here: ")
        self.fb_client = facebook.GraphAPI(access_token)

    def authorize_google_client(self):
        print("\nNote: Valid Google API tokens can be obtained by going to\n" +
              "developers.google.com/oauthplayground/. Make sure the token\n" +
              "you generate has the scope https://picasaweb.google.com/data/,\n" +
              "or choose Picasa Web v2 from the list.\n")
        access_token = raw_input("Enter a valid Google API token here: ")
        self.gd_client = gdata.photos.service.PhotosService(email=self.email,
                                                  additional_headers=
                                                  { 'Authorization' : 'Bearer %s' %
                                                access_token })

    def find_album(self, album_name):
        print("Defined in classes that inherit from the Hopper class")

    def list_album_photos(self, album):
        print("Defined in classes that inherit from the Hopper class")

    def create_album(self, album):
        print("Defined in classes that inherit from the Hopper class")

    def hop(self, photos, upload_url):
        print("Defined in classes that inherit from the Hopper class")


class FacebookHopper(Hopper):

    def find_album(self, album_name):
        user = self.fb_client.get_object(id="me")
        user_albums = self.fb_client.get_connections(user["id"], "albums")["data"]
        album_names = [album["name"] for album in user_albums]
        return user_albums[album_names.index(album_name)]

    def list_album_photos(self, album):
        album_page = self.fb_client.get_connections(album["id"], "photos")
        album_photos = album_page["data"]
        while True:
            try:
                # Attempt to get the next page of photos
                album_page = requests.get(album_page["paging"]["next"]).json()
                for photo in album_page["data"]:
                    album_photos.append(photo)
            except KeyError:
                # There are no more pages (album_page["paging"]["next"] throws KeyError)
                break
        return album_photos

    def create_album(self, album):
        try:
            album_summary = album["description"]
        except KeyError:
            album_summary = "Hopped from Facebook to Google Photos using Photo Hopper"
        gphoto_album = self.gd_client.InsertAlbum(title=album["name"], summary=album_summary)
        print("\nNew Google Photos album '%s' initialized\n" % album["name"])
        return '/data/feed/api/user/%s/albumid/%s' % ('default', gphoto_album.gphoto_id.text)

    def hop(self, photos, upload_url):
        for i in range(len(photos)):
            photo = photos[i]
            print("Hopping photo %s of %s" % (i + 1, len(photos)))
            try:
                photo_caption = photo["name"]
            except KeyError:
                photo_caption = "Doing the thing."
            open(self.storage_loc, 'wb').write(requests.get(photo["images"][0]["source"]).content)
            self.gd_client.InsertPhotoSimple(upload_url, photo["id"], photo_caption,
                                    self.storage_loc, content_type='image/jpeg')
        os.remove(self.storage_loc)
