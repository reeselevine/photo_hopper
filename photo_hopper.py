import os
import urllib
import requests
import httplib2

import yaml
import facebook
import gdata.photos.service
import gdata.media

from oauth2client.file import Storage
from oauth2client.client import flow_from_clientsecrets
from oauth2client import tools

def load_config():
    config = yaml.load(open("config.yaml", 'r'))
    return config

def facebook_client(access_token):
    return facebook.GraphAPI(access_token)

def google_data_client(credential_file, client_secrets_file, user_email):
    storage = Storage(credential_file)
    credentials = storage.get()
    if credentials is None or credentials.invalid:
        flags = tools.argparser.parse_args(args=[])
        flow = flow_from_clientsecrets(client_secrets_file, scope=["https://picasaweb.google.com/data/"])
        credentials = tools.run_flow(flow, storage, flags)
    if credentials.access_token_expired:
        credentials.refresh(httplib2.Http())
    return gdata.photos.service.PhotosService(email=user_email,
                                              additional_headers={'Authorization' : 'Bearer %s' % credentials.access_token})    

def facebook_album(fb_client, album_name):
    user = fb_client.get_object(id="me")
    user_albums = fb_client.get_connections(user["id"], "albums")["data"]
    album_names = [album["name"] for album in user_albums]
    return user_albums[album_names.index(album_name)]


def facebook_album_photos(fb_client, album):
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
    print "New Google Photos album initialized"
    return '/data/feed/api/user/%s/albumid/%s' % ('default', gphoto_album.gphoto_id.text)

def hop_photos(gd_client, photos, url, storage_location):
    for i in range(len(photos)):
        photo = photos[i]
        print "Transferring photo %s of %s" % (i + 1, len(photos))
        try:
            photo_caption = photo["name"]
        except KeyError:
            photo_caption = "Doing the thing."
        urllib.urlretrieve(photo["images"][0]["source"], storage_location)
        gd_client.InsertPhotoSimple(url, photo["id"], photo_caption,
                                    storage_location, content_type='image/jpeg')
    os.remove(storage_location)

def main():
    config = load_config()
    fb_client = facebook_client(config['facebook']['access_token'])
    gd_client = google_data_client(config['google']['cred_file'],
                                   config['google']['secrets_file'],
                                   config['google']['email'])
    fb_album = facebook_album(fb_client, config['album_name'])
    fb_photos = facebook_album_photos(fb_client, fb_album)
    gphoto_url = create_gphotos_album(gd_client, fb_album)
    hop_photos(gd_client, fb_photos, gphoto_url, config["storage_loc"])
    print "All done!"

if __name__ == "__main__":
    main()
