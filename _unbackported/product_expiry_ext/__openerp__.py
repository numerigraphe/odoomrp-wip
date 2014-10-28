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

{
    "name": "Products Expiry Date Extension",
    "version": "1.0",
    "depends": ["stock", "product_expiry"],
    "author": "OdooMRP team",
    "contributors": [
        "Juan Ignacio Úbeda <juanignacioubeda@avanzosc.es>",
    ],
    "category": "Custom Module",
    "website": "http://www.odoomrp.com",
    "complexity": "normal",
    "summary": "",
    "description": """
This module color lines in list of production lots based on expiration dates:

* Normal : Green color
* In alert : Blue color
* To remove : Yellow color
* After the 'Best Before' : Orange color
* Expired : Red color
    """,
    "images": [],
    "data": ["views/production_lot_ext_view.xml",
             "wizard/stock_transfer_details_view.xml"],
    "qweb": [],
    "demo": [],
    "test": [],
    "installable": True,
    "auto_install": False,
}
