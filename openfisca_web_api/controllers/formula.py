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


"""Formula controller"""


import collections
import datetime

import numpy as np
from openfisca_core import periods, simulations

from .. import contexts, conv, model, wsgihelpers


N_ = lambda message: message


@wsgihelpers.wsgify
def api1_formula(req):
    ctx = contexts.Ctx(req)
    headers = wsgihelpers.handle_cross_origin_resource_sharing(ctx)

    tax_benefit_system = model.tax_benefit_system

    requested_column, error = conv.pipe(
        conv.cleanup_line,
        conv.test_in(tax_benefit_system.column_by_name),
        conv.function(lambda column_name: tax_benefit_system.column_by_name[column_name]),
        conv.test(lambda column: column.formula_class is not None, error = N_(u"Variable is not a formula")),
        conv.not_none,
        )(req.urlvars.get('name'), state = ctx)
    if error is not None:
        return wsgihelpers.respond_json(ctx,
            collections.OrderedDict(sorted(dict(
                apiVersion = 1,
                error = collections.OrderedDict(sorted(dict(
                    code = 400,  # Bad Request
                    errors = [conv.jsonify_value(error)],
                    message = ctx._(u'Invalid formula name in request URL'),
                    ).iteritems())),
                method = req.script_name,
                params = req.body,
                url = req.url.decode('utf-8'),
                ).iteritems())),
            headers = headers,
            )

    params = req.GET
    inputs = dict(params)
    fields = dict(
        (column.name, column.input_to_dated_python)
        for column in tax_benefit_system.column_by_name.itervalues()
        )
    fields['period'] = conv.pipe(
        periods.json_or_python_to_period,
        conv.default(periods.period('month', datetime.date.today())),
        conv.function(lambda period: period.offset('first-of')),
        )
    data, errors = conv.pipe(
        conv.struct(
            fields,
            drop_none_values = True,
            ),
        )(params, state = ctx)
    if errors is not None:
        return wsgihelpers.respond_json(ctx,
            collections.OrderedDict(sorted(dict(
                apiVersion = 1,
                context = inputs.get('context'),
                error = collections.OrderedDict(sorted(dict(
                    code = 400,  # Bad Request
                    errors = [conv.jsonify_value(errors)],
                    message = ctx._(u'Bad parameters in request'),
                    ).iteritems())),
                method = req.script_name,
                params = inputs,
                url = req.url.decode('utf-8'),
                ).iteritems())),
            headers = headers,
            )

    period = data.pop('period')
    simulation = simulations.Simulation(
        debug = False,
        period = period,
        tax_benefit_system = tax_benefit_system,
        )
    # Initialize entities, assuming there is only one person and one of each other entities ("familles",
    # "foyers fiscaux", etc).
    persons = None
    for entity in simulation.entity_by_key_plural.itervalues():
        entity.count = 1
        entity.roles_count = 1
        entity.step_size = 1
        if entity.is_persons_entity:
            persons = entity
    # Link person to its entities using ID & role.
    for entity in simulation.entity_by_key_plural.itervalues():
        if not entity.is_persons_entity:
            holder = persons.get_or_new_holder(entity.index_for_person_variable_name)
            holder.set_array(period, np.array([0]))
            holder = persons.get_or_new_holder(entity.role_for_person_variable_name)
            holder.set_array(period, np.array([0]))
    # Inject all variables from query string into arrays.
    for column_name, value in data.iteritems():
        column = tax_benefit_system.column_by_name[column_name]
        entity = simulation.entity_by_key_plural[column.entity_key_plural]
        holder = entity.get_or_new_holder(column_name)
        holder.set_array(period, np.array([value], dtype = column.dtype))

    requested_dated_holder = simulation.compute(requested_column.name)

    return wsgihelpers.respond_json(ctx,
        collections.OrderedDict(sorted(dict(
            apiVersion = 1,
            # context = data['context'],
            method = req.script_name,
            params = inputs,
            url = req.url.decode('utf-8'),
            value = requested_dated_holder.to_value_json()[0],  # We have only one person => Unwrap the array.
            ).iteritems())),
        headers = headers,
        )