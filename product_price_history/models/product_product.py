# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

from openerp import models, fields, api
from openerp.addons import decimal_precision as dp

from .product_price import PRODUCT_FIELD_HISTORIZE


class ProductProduct(models.Model):
    _inherit = "product.product"

    cost_price = fields.Float(
        string="Variant Cost Price", digits=dp.get_precision('Product Price'),
        groups="base.group_user", company_dependent=True)

    @api.one
    def _set_cost_price(self, value):
        ''' Store the cost price change in order to be able to retrieve the
        cost of a product for a given date'''
        price_history_obj = self.env['product.price.history']
        user_company = self.env.user.company_id.id
        company_id = self.env.context.get('force_company', user_company)
        price_history_obj.create({
            'product_template_id': self.product_tmpl_id.id,
            'product': self.id,
            'cost': value,
            'company_id': company_id,
        })

    @api.model
    def create(self, values):
        product = super(ProductProduct, self).create(values)
        product._set_cost_price(product.cost_price)
        return product

    @api.multi
    def write(self, values):
        if 'cost_price' in values:
            for product in self:
                product._set_cost_price(values['cost_price'])
        return super(ProductProduct, self).write(values)

    @api.multi
    def open_product_historic_prices(self):
        product_tmpl_ids = self.env['product.template']
        for product in self:
            product_tmpl_ids |= product.product_tmpl_id
        res = self.env['ir.actions.act_window'].for_xml_id(
            'product_price_history', 'action_price_history')
        res['domain'] = ((res.get('domain', []) or []) +
                         [('product_template_id', 'in', product_tmpl_ids.ids)]
                         + [('product', 'in', self.ids)])
        return res

    @api.multi
    def read(self, fields, load='_classic_read'):
        if fields:
            fields.append('id')
        results = super(ProductProduct, self).read(fields, load=load)
        # Note if fields is empty => read all, so look at history table
        if not fields or any([f in PRODUCT_FIELD_HISTORIZE for f in fields]):
            p_history = self.env['product.price.history']
            company_id = (self.env.context.get('company_id', False) or
                          self.env.user.company_id.id)
            # if fields is empty we read all price fields
            if not fields:
                p_fields = PRODUCT_FIELD_HISTORIZE
            # Otherwise we filter on price fields asked in read
            else:
                p_fields = [f for f in PRODUCT_FIELD_HISTORIZE if f in fields]
            prod_prices = p_history._get_historic_price(
                product_ids=self.ids, company_id=company_id,
                datetime=self.env.context.get('to_date', False),
                field_names=p_fields)
            if prod_prices:
                for result in results:
                    dict_value = prod_prices[result['id']]
                    result.update(dict_value)
        return results
