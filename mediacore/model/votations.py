"""
Votation Model
"""
from datetime import datetime
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Unicode, DateTime, Integer
from sqlalchemy.orm import mapper, Query

from mediacore.model.meta import DBSession, metadata
from mediacore.plugin import events

votations = Table('votations', metadata,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('media_id', Integer, ForeignKey('media.id', onupdate='CASCADE', ondelete='CASCADE')),
    Column('user_name', Unicode(16), nullable=False),
    Column('likes', Integer, default=0, nullable=False),
    Column('dislikes', Integer, default=0, nullable=False),
    Column('votation_date', DateTime, default=datetime.now, nullable=False),
    mysql_engine='InnoDB',
    mysql_charset='utf8',
)

class VotationQuery(Query):
    def get_votations(self, media_id=None, user_name=None):
        return self.filter(Votation.media_id == media_id).filter(Votation.user_name == user_name)
        
    def get_votations_by_user_name(self, user_name=True):
        return self.filter(Votation.user_name == user_name)

    def get_votations_by_media_id(self, media_id=True):
        return self.filter(Votation.media_id == media_id)


class Votation(object):
    """Votation Model
    """

    query = DBSession.query_property(VotationQuery)

    def __repr__(self):
        return '<Votation: %r media=%r user=%r>' % (self.id, self.media_id, self.user_name)

    def __unicode__(self):
        return 'Votation %r' % self.id

    def increment_likes(self):
        self.likes += 1
        return self.likes

    def increment_dislikes(self):
        self.dislikes += 1
        return self.dislikes

    def _get_parent(self):
        return self.media or None
    def _set_parent(self, parent):
        self.media = parent
    parent = property(_get_parent, _set_parent, None, """
        The object this Votation belongs to, provided for convenience mostly.
        If the parent has not been eagerloaded, a query is executed automatically.
    """)


mapper(Votation, votations, order_by=votations.c.id, extension=events.MapperObserver(events.Votation), properties={})
