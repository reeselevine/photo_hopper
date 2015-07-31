import yaml
import facebook
import gdata.photos.service
import gdata.media
import gdata.geo
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
gd_client = gdata.photos.service.PhotosService(
    additional_headers={'Authorization' : 'Bearer %s' % credentials.access_token})


# get the list of photos we want to send to google photos from facebook
user = fb_graph.get_object(id="me")
user_albums = fb_graph.get_connections(user["id"], "albums")["data"]
album_names = [album["name"] for album in user_albums]
fb_album = user_albums[album_names.index(config["album_name"])]
fb_album_photos = fb_graph.get_connections(fb_album["id"], "photos")

# create a new album on Google Photos
gp_album = gd_client.InsertAlbum(title=fb_album["name"], summary=fb_album["description"])

