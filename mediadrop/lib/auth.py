# This file is a part of MediaCore, Copyright 2009 Simple Station Inc.
#
# MediaCore is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# MediaCore is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Auth-related helpers

Provides a custom request classifier for repoze.who to allow for Flash uploads.
"""

from repoze.who.classifiers import default_request_classifier
from webob.request import Request

from mediadrop.model.meta import DBSession
from mediadrop.model import Group, Permission


__all__ = ['add_auth', 'classifier_for_flash_uploads']


def add_auth(app, config):
    """Add authentication and authorization middleware to the ``app``."""
    from acoi.mediacore.auth import setup_acoi_auth
    return setup_acoi_auth(app, Group, Permission, DBSession,
                cookie_secret=config['sa_auth.cookie_secret'],
                plone_url=config.get('auth.plone_url', ''),
            )


def classifier_for_flash_uploads(environ):
    """Normally classifies the request as browser, dav or xmlpost.

    When the Flash uploader is sending a file, it appends the authtkt session
    ID to the POST data so we spoof the cookie header so that the auth code
    will think this was a normal request. In the process, we overwrite any
    pseudo-cookie data that is sent by Flash.

    TODO: Currently overwrites the HTTP_COOKIE, should ideally append.
    """
    classification = default_request_classifier(environ)
    if classification == 'browser' \
    and environ['REQUEST_METHOD'] == 'POST' \
    and 'Flash' in environ.get('HTTP_USER_AGENT', ''):
        session_key = environ['repoze.who.plugins']['cookie'].cookie_name
        # Construct a temporary request object since this is called before
        # pylons.request is populated. Re-instantiation later comes cheap.
        request = Request(environ)
        try:
            session_id = request.str_POST[session_key]
            environ['HTTP_COOKIE'] = '%s=%s' % (session_key, session_id)
        except KeyError:
            pass
    return classification
