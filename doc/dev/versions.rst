==================
Migration versions
==================


VERSION 54 (Handle Voting feature on media)
-------------------------------------------

Migrate mediacore to version #54, you have to::
1. remove entry in "migrate_versions" table into db
2. run command : $ bin/paster setup-app --name=mediacore_main etc/development.ini

Now You have one new table "votes" into db.
User preferences will be stored into this table, in following format::
<id>, <username>, <media_id>, <like>(1 if user likes this media, 0 otherwise), <dislike>(1 if user dislikes this media, 0 otherwise), <date>(current timestamp)

On any media object::
1. if current user is anonymous like/dislike buttons on media_player bar are hidden (only authenticated users can vote).
2. if the user is authenticated but did not make any preference, like/dislike buttons are visible.
3. If the user is authenticated and has made his preference, it will be stored in a new entry in the "votes" table (as described above).

.. note::
    If an anonyous user tries to call url http://<media-url>/rate?up=1 (or ?down=1) directly from his browser, an "Unouthorized Error" will be returned.

    Votes are stored both on vote table and media table in order to maintain the
    original voting feature at the same way than before.
