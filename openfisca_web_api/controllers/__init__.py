# -*- coding: utf-8 -*-


"""Controllers"""


import collections

from . import calculate, entities, field, fields, formula, graph, parameters, reforms, simulate, swagger, variables
from .. import contexts, urls, wsgihelpers, environment


router = None


@wsgihelpers.wsgify
def index(req):
    ctx = contexts.Ctx(req)
    headers = wsgihelpers.handle_cross_origin_resource_sharing(ctx)

    return wsgihelpers.respond_json(ctx,
        collections.OrderedDict(sorted(dict(
            apiVersion = environment.country_package_version,
            message = u'Welcome, this is OpenFisca Web API.',
            method = req.script_name,
            ).iteritems())),
        headers = headers,
        )


def make_router():
    routePrefix = '^/api/{}/'.format(environment.country_package_version)

    """Return a WSGI application that searches requests to controllers """
    global router
    routings = [
        ('GET', '^/$', index),
        ('GET', '^/api/?$', index),
        ('POST', routePrefix + 'calculate/?$', calculate.api1_calculate),
        ('GET', routePrefix + 'entities/?$', entities.api1_entities),
        ('GET', routePrefix + 'field/?$', field.api1_field),
        ('GET', routePrefix + 'fields/?$', fields.api1_fields),
        ('GET', routePrefix + 'formula/2/(?:(?P<period>[A-Za-z0-9:-]*)/)?(?P<names>[A-Za-z0-9_+-]+)/?$', formula.api2_formula),
        ('GET', routePrefix + 'formula/(?P<name>[^/0-9][^/]+)/?$', formula.api1_formula),
        ('GET', routePrefix + 'graph/?$', graph.api1_graph),
        ('GET', routePrefix + 'parameters/?$', parameters.api1_parameters),
        ('GET', routePrefix + 'reforms/?$', reforms.api1_reforms),
        ('POST', routePrefix + 'simulate/?$', simulate.api1_simulate),
        ('GET', routePrefix + 'swagger$', swagger.api1_swagger),
        ('GET', routePrefix + 'variables/?$', variables.api1_variables),
        ]
    router = urls.make_router(*routings)
    return router
