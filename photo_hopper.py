import yaml
import facebook
import requests
import urllib
import os
import gdata.photos.service
import gdata.media
import gdata.geo
import httplib2
# import gdata.service
from oauth2client.file import Storage
from oauth2client.client import flow_from_clientsecrets
from oauth2client.tools import run

with open("config.yaml", 'r') as stream:
    config = yaml.load(stream)

# authenticate for both google and facebook
fb_graph = facebook.GraphAPI(config["facebook"]["access_token"])

storage = Storage("creds.dat")
credentials = storage.get()
if credentials is None or credentials.invalid:
    flags = tools.argparser.parse_args(args=[])
    flow = flow_from_clientsecrets("client_secrets.json", scope=["https://picasaweb.google.com/data/"])
    credentials = run(flow, storage, flags)
if credentials.access_token_expired:
    credentials.refresh(httplib2.Http())
gd_client = gdata.photos.service.PhotosService(email=config["google"]["email"],
    additional_headers={'Authorization' : 'Bearer %s' % credentials.access_token})


# get the list of photos we want to send to google photos from facebook
user = fb_graph.get_object(id="me")
user_albums = fb_graph.get_connections(user["id"], "albums")["data"]
album_names = [album["name"] for album in user_albums]
fb_album = user_albums[album_names.index(config["album_name"])]
fb_album_page = fb_graph.get_connections(fb_album["id"], "photos")
fb_album_photos = fb_album_page["data"]

while True:
    try:
        # Attempt to get the next page of photos
        fb_album_page = requests.get(fb_album_page["paging"]["next"]).json()
        for fb_photo in fb_album_page["data"]:
            fb_album_photos.append(fb_photo)
    except KeyError:
        # There are no more pages (fb_album_page["paging"]["next"] returns KeyError)
        break
for photo in fb_album_photos:
    print photo["images"][0]["source"]
    

# create a new album on Google Photos
try:
    album_summary = album["description"]
except KeyError:
    album_summary = "Hopped from Facebook to Google Photos using Photo Hopper"
    
gphoto_album = gd_client.InsertAlbum(title=fb_album["name"], summary=album_summary)
gphoto_album_url = '/data/feed/api/user/%s/albumid/%s' % ('default', gphoto_album.gphoto_id.text)

for photo in fb_album_photos:
    try:
        photo_caption = photo["name"]
    except KeyError:
        photo_caption = "Doing the thing."

    urllib.urlretrieve(photo["images"][0]["source"], "/tmp/photo_hopper.jpg")
    gd_client.InsertPhotoSimple(gphoto_album_url, photo["id"], photo_caption,
                                "/tmp/photo_hopper.jpg", content_type='image/jpeg')

os.remove("/tmp/photo_hopper.jpg")
    
