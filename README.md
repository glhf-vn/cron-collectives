# mangaGLHF's collection of cron-scripts

Install the dependencies:
`pip install python-dotenv bs4 babel discord_webhook selenium webdriver-manager pandas lxml`

For `upload.py` script, install optional `cloudinary`, `pillow` and `google` dependencies:
`pip install --upgrade cloudinary Pillow google-api-python-client google-auth-httplib2 google-auth-oauthlib`

.env required field
```
DISCORD_PUBLISHER_WEBHOOK=
DISCORD_TIKI_WEBHOOK=
DISCORD_FAHASA_WEBHOOK=

DISCORD_IPM_REGISTRY_WEBHOOK=
DISCORD_TRE_REGISTRY_WEBHOOK=
DISCORD_KIM_REGISTRY_WEBHOOK=

DISCORD_UPDATES_WEBHOOK=

CLOUDINARY_NAME=
CLOUDINARY_KEY=
CLOUDINARY_SECRET=

GOOGLE_API_KEY=
```