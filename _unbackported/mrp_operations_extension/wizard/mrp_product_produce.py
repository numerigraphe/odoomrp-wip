
# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2008-2013 AvanzOSC S.L. (Mikel Arregi) All Rights Reserved
#
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

from openerp import fields, models


class MrpWorkOrderProduce(models.TransientModel):

    _name = "mrp.work.order.produce"

    def default_get(self, cr, uid, fields, context=None):
        a = super(MrpWorkOrderProduce, self).default_get(
            cr, uid, fields, context=context)
        work = self.pool['mrp.production.workcenter.line'].browse(
            cr, uid, context.get('active_ids'), context=context)[0]
        a.update({'final_product': work.do_production})
        return a

    def _get_product_id(self):
        """ To obtain product id
        @return: id
        """
        prod = False
        if self.env.context.get("active_id"):
            work_line = self.env['mrp.production.workcenter.line'].browse(
                self.env.context.get("active_id"))
            prod = work_line.production_id
        return prod and prod.product_id or False

    def _get_track(self):
        prod = self._get_product_id()
        return prod and prod.track_production or False

    def do_produce(self, cr, uid, ids, context=None):
        work_line = self.pool['mrp.production.workcenter.line'].browse(
            cr, uid, context.get("active_id"), context=context)
        production_id = work_line.production_id.id
        assert production_id
        data = self.browse(cr, uid, ids[0], context=context)
        self.pool['mrp.production'].action_produce(
            cr, uid, production_id, False, data.mode, data, context=context)
        return {}

    def do_consume(self, cr, uid, ids, context=None):
        work_line = self.pool['mrp.production.workcenter.line'].browse(
            cr, uid, context.get("active_id"), context=context)
        production_id = work_line.production_id.id
        assert production_id
        data = self.browse(cr, uid, ids[0], context=context)
        self.pool['mrp.production'].action_produce(
            cr, uid, production_id, False, 'consume', data, context=context)
        return {}

    def do_consume_produce(self, cr, uid, ids, context=None):
        work_line = self.pool['mrp.production.workcenter.line'].browse(
            cr, uid, context.get("active_id"), context=context)
        production_id = work_line.production_id.id
        assert production_id
        data = self.browse(cr, uid, ids[0], context=context)
        self.pool['mrp.production'].action_produce(
            cr, uid, production_id, False, 'consume_produce', data,
            context=context)
        return {}

    def on_change_qty(self, cr, uid, ids, product_qty, consume_lines,
                      context=None):
        """
            When changing the quantity of products to be producedit will
            recalculate the number of raw materials needed according to
            the scheduled products and the already consumed/produced products
            It will return the consume lines needed for the products
            to be produced which the user can still adapt
        """
        prod_obj = self.pool["mrp.production"]
        work_line = self.pool['mrp.production.workcenter.line'].browse(
            cr, uid, context.get("active_id"), context=context)
        production = work_line.production_id
        consume_lines = []
        new_consume_lines = []
        if product_qty > 0.0:
            consume_lines = prod_obj._calculate_qty(
                cr, uid, production, product_qty=product_qty, context=context)
        line_ids = [i.product_id.id for i in work_line.product_line]
        for consume in consume_lines:
            if consume['product_id'] in line_ids:
                new_consume_lines.append([0, False, consume])
        return {'value': {'consume_lines': new_consume_lines}}

    def _get_product_qty(self):
        """ To obtain product quantity
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param context: A standard dictionary
        @return: Quantity
        """
        work_line = self.env['mrp.production.workcenter.line'].browse(
            self.env.context.get("active_id"))
        prod = work_line.production_id
        done = 0.0
        for move in prod.move_created_ids2:
            if move.product_id == prod.product_id:
                if not move.scrapped:
                    done += move.product_qty
        return (prod.product_qty - done) or prod.product_qty

    product_id = fields.Many2one('product.product',
                                 string='Product', default=_get_product_id)
    product_qty = fields.Float('Select Quantity',
                               digits=(12, 6), required=True,
                               default=_get_product_qty)
    mode = fields.Selection([('consume_produce', 'Consume & Produce'),
                             ('consume', 'Consume Only')],
                            string='Mode', required=True,
                            default='consume')
    lot_id = fields.Many2one('stock.production.lot', 'Lot')
    consume_lines = fields.One2many('mrp.product.produce.line',
                                    'work_produce_id',
                                    string='Products Consumed')
    track_production = fields.Boolean('Track production', default=_get_track)

    final_product = fields.Boolean(string='Final Product to Stock')


class mrp_product_produce_line(models.TransientModel):
    _inherit = "mrp.product.produce.line"

    work_produce_id = fields.Many2one('mrp.work.order.produce')
