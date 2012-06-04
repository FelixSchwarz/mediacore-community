from sqlalchemy import *
from migrate import *

metadata = MetaData()
from datetime import datetime

from mediacore.model.auth import users
from mediacore.model.media import media
from mediacore.model.votes import votes


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind migrate_engine
    # to your metadata
    metadata.bind = migrate_engine
    votes.create(checkfirst=True)

def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    metadata.bind = migrate_engine
    votes.drop(checkfirst=True)