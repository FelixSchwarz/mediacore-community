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
Library Utilities

"""
import math
import os
import shutil
from datetime import datetime
from urlparse import urlparse

from pylons import app_globals, config, request, url as pylons_url
from webob.exc import HTTPFound

__all__ = [
    'calculate_popularity',
    'delete_files',
    'merge_dicts',
    'redirect',
    'url',
    'url_for',
]

def url(*args, **kwargs):
    """Compose a URL with :func:`pylons.url`, all arguments are passed."""
    return _generate_url(pylons_url, *args, **kwargs)

def url_for(*args, **kwargs):
    """Compose a URL :func:`pylons.url.current`, all arguments are passed."""
    return _generate_url(pylons_url.current, *args, **kwargs)

# Mirror the behaviour you'd expect from pylons.url
url.current = url_for

def _generate_url(url_func, *args, **kwargs):
    """Generate a URL using the given callable."""
    # Convert unicode to str utf-8 for routes
    def to_utf8(value):
        if isinstance(value, unicode):
            return value.encode('utf-8')
        return value

    if args:
        args = [to_utf8(val) for val in args]
    if kwargs:
        kwargs = dict((key, to_utf8(val)) for key, val in kwargs.iteritems())

    # TODO: Rework templates so that we can avoid using .current, and use named
    # routes, as described at http://routes.groovie.org/manual.html#generating-routes-based-on-the-current-url
    # NOTE: pylons.url is a StackedObjectProxy wrapping the routes.url method.
    url = url_func(*args, **kwargs)

    # If the proxy_prefix config directive is set up, then we need to make sure
    # that the SCRIPT_NAME is prepended to the URL. This SCRIPT_NAME prepending
    # is necessary for mod_proxy'd deployments, and for FastCGI deployments.
    # XXX: Leaking abstraction below. This code is tied closely to Routes 1.12
    #      implementation of routes.util.URLGenerator.__call__()
    # If the arguments given didn't describe a raw URL, then Routes 1.12 didn't
    # prepend the SCRIPT_NAME automatically--we'll need to feed the new URL
    # back to the routing method to prepend the SCRIPT_NAME.
    prefix = config.get('proxy_prefix', None)
    if prefix:
        if args:
            named_route = config['routes.map']._routenames.get(args[0])
            protocol = urlparse(args[0]).scheme
            static = not named_route and (args[0][0]=='/' or protocol)
        else:
            static = False
            protocol = ''

        if not static:
            if kwargs.get('qualified', False):
                offset = len(urlparse(url).scheme+"://")
            else:
                offset = 0
            path_index = url.index('/', offset)
            url = url[:path_index] + prefix + url[path_index:]

    return url

def redirect(*args, **kwargs):
    """Compose a URL using :func:`url_for` and raise a redirect.

    :raises: :class:`webob.exc.HTTPFound`
    """
    url = url_for(*args, **kwargs)
    found = HTTPFound(location=url)
    raise found.exception

def delete_files(paths, subdir=None):
    """Move the given files to the 'deleted' folder, or just delete them.

    If the config contains a deleted_files_dir setting, then files are
    moved there. If that setting does not exist, or is empty, then the
    files will be deleted permanently instead.

    :param paths: File paths to delete. These files do not necessarily
        have to exist.
    :type paths: iterable
    :param subdir: A subdir within the configured deleted_files_dir to
        move the given files to. If this folder does not yet exist, it
        will be created.
    :type subdir: str or ``None``

    """
    deleted_dir = config.get('deleted_files_dir', None)
    if deleted_dir and subdir:
        deleted_dir = os.path.join(deleted_dir, subdir)
    if deleted_dir and not os.path.exists(deleted_dir):
        os.mkdir(deleted_dir)
    for path in paths:
        if path and os.path.exists(path):
            if deleted_dir:
                shutil.move(path, deleted_dir)
            else:
                os.remove(path)

def merge_dicts(dst, *srcs):
    """Recursively merge two or more dictionaries.

    Code adapted from Manuel Muradas' example at
    http://code.activestate.com/recipes/499335-recursively-update-a-dictionary-without-hitting-py/
    """
    for src in srcs:
        stack = [(dst, src)]
        while stack:
            current_dst, current_src = stack.pop()
            for key in current_src:
                if key in current_dst \
                and isinstance(current_src[key], dict) \
                and isinstance(current_dst[key], dict):
                    stack.append((current_dst[key], current_src[key]))
                else:
                    current_dst[key] = current_src[key]
    return dst

def calculate_popularity(publish_date, score):
    """Calculate how 'hot' an item is given its response since publication.

    In our ranking algorithm, being base_life_hours newer is equivalent
    to having log_base times more votes.

    :type publish_date: datetime.datetime
    :param publish_date: The date of publication. An older date reduces
        the popularity score.
    :param int score: The number of likes, dislikes or likes - dislikes.
    :rtype: int
    :returns: Popularity points.

    """
    settings = request.settings
    log_base = int(settings['popularity_decay_exponent'])
    base_life = int(settings['popularity_decay_lifetime']) * 3600
    # FIXME: The current algorithm assumes that the earliest publication
    #        date is January 1, 2000.
    if score > 0:
        sign = 1
    elif score < 0:
        sign = -1
    else:
        sign = 0
    delta = publish_date - datetime(2000, 1, 1) # since January 1, 2000
    t = delta.days * 86400 + delta.seconds
    popularity = math.log(max(abs(score), 1), log_base) + sign * t / base_life
    return max(int(popularity), 0)


def check_user_authentication(request):
    # we have to check if current user is anonymous or authenticated
    if hasattr(request, 'identity'):
        userid = request.identity['repoze.who.userid']
    else:
        request_identity = request.environ.get('repoze.who.identity')
        if request_identity:
            # current user is authenticated
            userid = request_identity['repoze.who.userid']
        else:
            # current user is anonymous
            userid = None

    return userid


def get_authenticated_user(request):
    # we have to check if current user is anonymous or authenticated
    if hasattr(request, 'identity'):
        user = request.identity['repoze.who.userid']
        # XXX: do something here to get user data
    else:
        request_identity = request.environ.get('repoze.who.identity')
        if request_identity:
            # XXX: check if user is none?
            user = request_identity.get('user')
    return user
