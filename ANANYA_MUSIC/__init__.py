from ANANYA_MUSIC.core.bot import Ananya
from ANANYA_MUSIC.core.dir import dirr
from ANANYA_MUSIC.core.git import git
from ANANYA_MUSIC.core.userbot import Userbot
from ANANYA_MUSIC.misc import dbb, heroku

from SafoneAPI import SafoneAPI
from .logging import LOGGER

dirr()
git()
dbb()
heroku()

app = Ananya()
api = SafoneAPI()
userbot = Userbot()


from .platforms import *

Apple = AppleAPI()
Carbon = CarbonAPI()
SoundCloud = SoundAPI()
Spotify = SpotifyAPI()
Resso = RessoAPI()
Telegram = TeleAPI()
YouTube = YouTubeAPI()
