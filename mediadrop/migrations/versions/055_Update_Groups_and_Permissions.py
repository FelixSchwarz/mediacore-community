from datetime import datetime

from sqlalchemy import *
from migrate import *

from mediadrop.model.auth import permissions
from mediadrop.model.auth import groups
from mediadrop.model.auth import groups_permissions

metadata = MetaData()


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind migrate_engine
    # to your metadata
    metadata.bind = migrate_engine
    conn = migrate_engine.connect()

    # USERS SSO STUFF
    # see acoi.mediacore/README.txt
    perm_name = u'view'
    comment_perm_id = permissions.select().where(
        permissions.c.permission_name.match(perm_name)
    ).scalar()
    if not comment_perm_id:
        # add comment perm
        comment_perm_id = conn.execute(permissions.insert().values(
            permission_name=perm_name,
            description=u'Grants access to view site contents',
        )).inserted_primary_key[0]
        print 'created permission %s' % perm_name

    # get group
    group_name = u'users'
    group_id = groups.select().where(
        groups.c.group_name.match(group_name)
    ).scalar()
    if not group_id:
        # add comment perm
        group_id = conn.execute(groups.insert().values(
            group_name=group_name,
            display_name=u'Users',
        )).inserted_primary_key[0]
        print 'created group %s' % group_name

    # assign permission to group
    assignment = groups_permissions.select().where(
        groups_permissions.c.group_id.match(group_id),
        groups_permissions.c.permission_id.match(comment_perm_id),
    ).scalar()
    if not assignment:
        conn.execute(groups_permissions.insert().values(
            group_id=group_id,
            permission_id=comment_perm_id,
        ))
        print 'added permission %s to group %s' % (perm_name, group_name)

    # COMMENT STUFF
    # check for comment perm
    perm_name = u'comment'
    comment_perm_id = permissions.select().where(
        permissions.c.permission_name.match(perm_name)
    ).scalar()
    if not comment_perm_id:
        # add comment perm
        comment_perm_id = conn.execute(permissions.insert().values(
            permission_name=perm_name,
            description=u'Grants access to add comments',
        )).inserted_primary_key[0]
        print 'created permission %s' % perm_name

    # get group
    group_name = u'commenters'
    group_id = groups.select().where(
        groups.c.group_name.match(group_name)
    ).scalar()
    if not group_id:
        # add comment perm
        group_id = conn.execute(groups.insert().values(
            group_name=group_name,
            display_name=u'Commenters',
        )).inserted_primary_key[0]
        print 'created group %s' % group_name

    # assign permission to group
    assignment = groups_permissions.select().where(
        groups_permissions.c.group_id.match(group_id),
        groups_permissions.c.permission_id.match(comment_perm_id),
    ).scalar()
    if not assignment:
        conn.execute(groups_permissions.insert().values(
            group_id=group_id,
            permission_id=comment_perm_id,
        ))
        print 'added permission %s to group %s' % (perm_name, group_name)


def downgrade(migrate_engine):
    raise NotImplementedError()
