# Nextcloud HEIC/WEBP converter
 
## Why?

I could not get HEIC/WEBP previews working correcly when using Nextcloud on FreeBSD.
So I made this script to convert them to jpg instead, which works fine for previews.

### How?

This Python script uses the WebDAV protocol to convert .heic/.webp files in a given Nextcloud folder to .jpg.
The script works by finding all .heic/.webp files in the specified folder, downloading each file, converting it to .jpg,
then re-uploading the new jpg file back to the same location in the Nextcloud server. The original .heic/.webp file is
subsequently deleted from the server.

#### Usage
Set up the environment variables in a `.env` file (see from `.env.example`):

```
NEXTCLOUD_DAV_ENDPOINT: Your Nextcloud WebDAV endpoint.
NEXTCLOUD_USERNAME: Your Nextcloud username.
NEXTCLOUD_PASSWORD: Your Nextcloud password.
NEXTCLOUD_FOLDER: The path of the Nextcloud folder you wish to convert files in.

```

You can run the script with Poetry:
`poetry run nextcloud_heic_webp_converter/main.py`

#### Requirements

You need `imagemagick` installed as this script relies on its `convert` command.
