# This file is a part of MediaCore CE (http://www.mediacorecommunity.org),
# Copyright 2009-2013 MediaCore Inc., Felix Schwarz and other contributors.
# For the exact contribution history, see the git revision log.
# The source code contained in this file is licensed under the GPLv3 or
# (at your option) any later version.
# See LICENSE.txt in the main project directory, for more information.

"""
Publicly Facing Media Controllers
"""
import logging

from pylons import request

from mediacore.forms.comments import PostCommentSchema
from mediacore.lib import helpers
from mediacore.lib.base import BaseController
from mediacore.lib.decorators import expose, observable
from mediacore.model import Media
from mediacore.plugin import events

log = logging.getLogger(__name__)

comment_schema = PostCommentSchema()


class EmbedFeaturedController(BaseController):
    """
    Embed Featured
    """

    @expose('players/iframe_featured.html')
    @observable(events.MediaController.embed_player)
    def index(self, w=None, h=None, **kwargs):

        published = Media.query.published()
        latest = published.order_by(Media.publish_on.desc())

        media = None
        featured_cat = helpers.get_featured_category()
        if featured_cat:
            media = latest.in_category(featured_cat).first()
        if not media:
            media = published.order_by(Media.popularity_points.desc()).first()

        request.perm.assert_permission(u'view', media.resource)

        return dict(
            media=media,
            width=w and int(w) or None,
            height=h and int(h) or None,
        )
