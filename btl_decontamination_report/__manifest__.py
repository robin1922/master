# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2016 BroadTech IT Solutions Pvt Ltd
#    (http://www.broadtech-innovations.com)
#    contact@broadtech-innovations.com
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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Decontamination Report',
    'version': '12.5',
    'category': 'General',
    'description': """
Test2 Pull Request
    """,
    'author': 'BroadTech IT Solutions Pvt Ltd.',
    'website': 'http://www.broadtech-innovations.com',
    'depends': ['btl_loaners_tracking','btl_sale_phase2'],
    'demo': [],
    'data': [
        'security/ir.model.access.csv',
        'views/decontamination_report_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    

}


