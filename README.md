# Usage #

## Simple ##
- Photo Hopper is ready to be run as a Docker container. If you have docker set up, simply run `docker run -it reeselevine/photo_hopper` on your command line and follow the instructions.
- Note: Generating temporary API keys does require you to have a developer account on both Facebook and Google

### More info ###
Photo Hopper needs to be run on Python 2 (preferably 2.7.10), due to limits on the Google Data APIs. If you want to run it outside of the docker environment, just make sure you install the python modules facebook-sdk, gdata, and requests. If you're using pip, just run
`pip install facebook-sdk gdata requests`

Photo Hopper also does not require any credentials to be embedded anywhere, which is nice for security and for use with public Docker images. All API keys generated from Google and Facebook's sandboxes expire after about one hour anyways, so even if someone does manage to find something in the docker container after it has been run, which is highly unlikely, the chances of them getting access to your photos is extremely slim.

## Background ##

I really like Google Photos, because of its free storage and great interface and assistant. But since it was only released a couple months ago, there's no official API for it, and no good way to export albums from Facebook to Google Photos. Sure, you can just mass download your photos and re-upload them on Google Photos, but I also wanted to preserve album structure, and I especially didn't want to have to rewrite all my captions. 

Luckily, Google Photos seems to be based on the same engine as Picasa Web, which I am sure they will retire at some point. Therefore, by interacting with the Picasa Web endpoints, Google Photos can be manipulated as well, creating albums and uploading photos. This is also pretty cool because it gives an inside look into Google's development practices, in a roundabout way.

It's not very fast, mostly because the Google Data API requires a file-like image location, and was rejecting links directly from Facebook. This means that the script has to download every image to the local machine and then re-upload it. Not pretty, but it's the best I think I can do at the moment.

This will probably be a temporary solution, at least until Google releases a new API for Google Photos, or direct uplading from Facebook, which could happen tomorrow or a year from now. But until then, this is my workaround, and hopefully someone out there finds it useful as well!

