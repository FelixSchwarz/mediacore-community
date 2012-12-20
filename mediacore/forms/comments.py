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

from formencode import Schema

from mediacore.forms import TextField, XHTMLValidator, email_validator
from mediacore.lib.i18n import N_

class PostCommentSchema(Schema):
    # name = TextField.validator(not_empty=True, maxlength=50,
    #     messages={'empty': N_('Please enter your name!')})
    # email = email_validator()
    body = XHTMLValidator(not_empty=True)
