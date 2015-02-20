# -*- coding: utf-8 -*-


# OpenFisca -- A versatile microsimulation software
# By: OpenFisca Team <contact@openfisca.fr>
#
# Copyright (C) 2011, 2012, 2013, 2014, 2015 OpenFisca Team
# https://github.com/openfisca
#
# This file is part of OpenFisca.
#
# OpenFisca is free software; you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# OpenFisca is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


"""Helpers for URLs"""


import re
import urllib
import urlparse

from biryani import strings
import webob

from . import contexts, wsgihelpers


application_url = None  # Set to req.application_url as soon as application is called.


def get_base_url(ctx, full = False):
    assert not(application_url is None and full), "Can't use full URLs when application_url is not inited."
    base_url = (application_url or u'').rstrip('/')
    if not full:
        # When a full URL is not requested, remove scheme and network location from it.
        base_url = urlparse.urlsplit(base_url).path
    return base_url


def get_full_url(ctx, *path, **query):
    path = [
        urllib.quote(unicode(sub_fragment).encode('utf-8'), safe = ',/:').decode('utf-8')
        for fragment in path
        if fragment
        for sub_fragment in unicode(fragment).split(u'/')
        if sub_fragment
        ]
    query = dict(
        (str(name), strings.deep_encode(value))
        for name, value in sorted(query.iteritems())
        if value not in (None, [], (), '')
        )
    return u'{0}/{1}{2}'.format(get_base_url(ctx, full = True), u'/'.join(path),
        ('?' + urllib.urlencode(query, doseq = True)) if query else '')


def get_url(ctx, *path, **query):
    path = [
        urllib.quote(unicode(sub_fragment).encode('utf-8'), safe = ',/:').decode('utf-8')
        for fragment in path
        if fragment
        for sub_fragment in unicode(fragment).split(u'/')
        if sub_fragment
        ]
    query = dict(
        (str(name), strings.deep_encode(value))
        for name, value in sorted(query.iteritems())
        if value not in (None, [], (), '')
        )
    return u'{0}/{1}{2}'.format(get_base_url(ctx), u'/'.join(path),
        ('?' + urllib.urlencode(query, doseq = True)) if query else '')


def make_router(*routings):
    """Return a WSGI application that dispatches requests to controllers """
    routes = []
    for routing in routings:
        methods, regex, app = routing[:3]
        if isinstance(methods, basestring):
            methods = (methods,)
        vars = routing[3] if len(routing) >= 4 else {}
        routes.append((methods, re.compile(unicode(regex)), app, vars))

    def router(environ, start_response):
        """Dispatch request to controllers."""
        req = webob.Request(environ)
        ctx = contexts.Ctx(req)

        split_path_info = req.path_info.split('/')
        if split_path_info[0]:
            # When path_info doesn't start with a "/" this is an error or a attack => Reject request.
            # An example of an URL with such a invalid path_info: http://127.0.0.1http%3A//127.0.0.1%3A80/result?...
            headers = wsgihelpers.handle_cross_origin_resource_sharing(ctx)
            return wsgihelpers.respond_json(ctx,
                dict(
                    apiVersion = 1,
                    error = dict(
                        code = 400,  # Bad Request
                        message = ctx._(u"Invalid path: {0}").format(req.path_info),
                        ),
                    ),
                headers = headers,
                )(environ, start_response)

        for methods, regex, app, vars in routes:
            match = regex.match(req.path_info)
            if match is not None:
                if methods is not None and req.method not in methods:
                    headers = wsgihelpers.handle_cross_origin_resource_sharing(ctx)
                    return wsgihelpers.respond_json(ctx,
                        dict(
                            apiVersion = 1,
                            error = dict(
                                code = 405,
                                message = ctx._(u"You cannot use HTTP {} to access this URL. Use one of {}.")
                                             .format(req.method, methods),
                                ),
                            ),
                        headers = headers,
                        )(environ, start_response)

                if getattr(req, 'urlvars', None) is None:
                    req.urlvars = {}
                req.urlvars.update(match.groupdict())
                req.urlvars.update(vars)
                req.script_name += req.path_info[:match.end()]
                req.path_info = req.path_info[match.end():]
                return app(req.environ, start_response)

        headers = wsgihelpers.handle_cross_origin_resource_sharing(ctx)
        return wsgihelpers.respond_json(ctx,
            dict(
                apiVersion = 1,
                error = dict(
                    code = 404,  # Not Found
                    message = ctx._(u"Path not found: {0}").format(req.path_info),
                    ),
                ),
            headers = headers,
            )(environ, start_response)

    return router


def relative_query(inputs, **query):
    inputs = inputs.copy()
    inputs.update(query)
    return inputs
