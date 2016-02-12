import logging
import os

from flask import abort
from flask import redirect
from flask import render_template
from flask import request
from flask import send_from_directory
from flask import url_for
from flask.views import MethodView

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse


from main import app
import utils
from sdk import constants

MB_HOMEPAGE = 'https://example.com'

log = logging.getLogger(__name__)

class IndexView(MethodView):
    """
    Index redirects to Mailbeaker home
    """

    def get(self):
        log.info('', extra = {
            'server':   'link',
            'view':     'index',
        })
        return redirect(MB_HOMEPAGE)


class LinkView(MethodView):
    """
    View for redirecting a link to the original url.
    """

    def get(self, link_jwt):
        log.info('', extra = {
            'server':   'link',
            'view':     'link',
            'event':    'started',
        })

        context = dict()
        action, redirect_url = utils.get_link_info(link_jwt)

        # Everything checks out.  Redirect directly to the URL.
        if action == constants.ACTION_PASS:
            return redirect(redirect_url)

        # Rule matches, requesting warning page.
        elif action == constants.ACTION_WARN:
            context = {
                'title':        "We've got a bad feeling about this.",
                'redirect_url': redirect_url,
            }

            return render_template('warn.html', **context)

        # Rule matches, requesting blocking page.
        elif action == constants.ACTION_BLOCK:
            url = urlparse(redirect_url)
            domain = url.netloc
            context = {
                'title': "We're stepping in to protect you.",
                'domain': domain
            }

            return render_template('block.html', **context)

        elif action == constants.ACTION_INVALID:
            # Invalid link. Might have been due to a JWT verification
            # failure.  We try decoding the JWT without verification
            # to see if we can get the info from it.

            return render_template('error.html', **context), 400
            # TODO remove the above and re-enable this after adding option to verify to SDK JWT checks
            """
            link_jwt = utils.decode_jwt_v1(link_jwt, verify=False)

            if link_jwt:
                redirect_url = link_jwt.get('u')

                context = {
                    'title': "There was an unexpected error with that link.",
                    'redirect_url': redirect_url,
                }
                return render_template('link_error.html', **context), 400

            else:
                context = {
                    'title': "We're sorry, but something went wrong.",
                }
                return render_template('error.html', **context), 400
            """
        return redirect(redirect_url)


class FaviconView(MethodView):

    def get(self):
        return send_from_directory(
            os.path.join(app.root_path, 'static'),
            'mailbeaker-ico.png',
            mimetype='image/vnd.microsoft.icon'
        )


###########
# URL Rules
###########

app.add_url_rule('/', view_func=IndexView.as_view('index'))
app.add_url_rule('/favicon.ico/', view_func=FaviconView.as_view('favicon'))
app.add_url_rule('/v1/<string:link_jwt>/', view_func=LinkView.as_view('links'))
