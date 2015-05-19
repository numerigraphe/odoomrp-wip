# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################
from openerp import models, fields, api


class ProductCategory(models.Model):
    _inherit = 'product.category'

    lot_default_locked = fields.Boolean(
        string='Block new Serial Numbers/lots',
        help='If checked, future Serial Numbers/lots will be created blocked '
             'by default')

    parent_lot_default_locked = fields.Boolean(
       string='Block new Serial Nb. (incl. parents)',
       compute='_get_parent_lot_default_locked', store=True,
       help='Checked automatically when "Block new Serial Numbers/lots" is '
            'checked on either this Category or one of its parents.')

    @api.one
    @api.depends('lot_default_locked', 'parent_id',
                 'parent_id.lot_default_locked', 'parent_id.parent_lot_default_locked')
    def _get_parent_lot_default_locked(self):
        """Locked (including categories)

        @return True when the category or one of the parents demand new lots
                to be locked"""
        self.parent_lot_default_locked = self.lot_default_locked or self.parent_id.lot_default_locked
