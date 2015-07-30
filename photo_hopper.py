import yaml
import facebook

# get the list of photos we want to send to google photos from facebook
with open("config.yaml", 'r') as stream:
    config = yaml.load(stream)

graph = facebook.GraphAPI(config["access_token"])

user = graph.get_object(id="me")
user_albums = graph.get_connections(user["id"], "albums")["data"]
album_names = [album["name"] for album in user_albums]
album = user_albums[album_names.index(config["album_name"])]

album_photos = graph.get_connections(album["id"], "photos")
