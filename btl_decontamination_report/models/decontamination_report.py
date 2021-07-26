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
import random
from datetime import datetime, date

from odoo.exceptions import UserError, ValidationError
from odoo.http import request
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo import api, fields, models, _
from odoo.tools import float_compare

class DecontaminationDescription(models.Model):
    _name = 'decontamination.description'
    _description = 'Decontamination Description'
    
    code = fields.Char('Code')
    name = fields.Char('Description', required=True)
    

class DecontaminationReport(models.Model):
    _name = 'decontamination.report'
    _inherit = ['mail.thread']
    _description = 'Decontamination Report'
    _order = 'name desc'
    
   
    name = fields.Char(string='Decontamination Report #', required=False, readonly=True, default='/', track_visibility='onchange', copy=False)
    report_confirm_date = fields.Datetime(string='Confirm Date', default= fields.Datetime.now(), track_visibility='onchange', copy=False)
    user_id = fields.Many2one('res.users', string='Responsible', required=True, default=lambda self: self.env.user.id, track_visibility='onchange', copy=True)
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm')], string='Status', required=True, readonly=True, default='draft',
                             index=True, track_visibility='onchange', copy=False)
    sr_prefix = fields.Char(string='Prefix', readonly=True, copy=False)
    decontamination_items_ids = fields.One2many('decontamination.report.line', 'decontamination_id', string="Decontamination Items", copy=True, track_visibility='onchange',)
    decontaminated = fields.Boolean(string='Decontaminated', default= False, copy=True, track_visibility='onchange',)
    decontaminated_id = fields.Many2one('decontamination.description', string='Decontaminated with', track_visibility='onchange',)

    
    
            
            
    def check_confirm(self):
        for decontaminate_rec in self:
            if not  decontaminate_rec.decontaminated:
                raise UserError(_('Please mark Item decontaminated'))
            if not decontaminate_rec.decontamination_items_ids:
                raise UserError(_('Add Decontamination lines to continue'))
            
            decontaminate_rec.action_confirm()
            
    def action_confirm(self):
        decontaminate_rec = self
        
        sr_name = 'DCRUSA-'
        today = datetime.today()
        day = today.strftime("%d")
        month = today.strftime("%m")
        year = str(today.year)
        sr_date = year + month + day
#         now = str(date.today()) + ' 00:00:00'
        sr_prefix = sr_name + sr_date
        todays_entries = self.env['decontamination.report'].search([('sr_prefix', '=', sr_prefix)])
#         todays_entries = self.env['decontamination.report'].search(cr, uid, [('create_date', '>=', now)])
        decontaminate_rec.write({'sr_prefix' : sr_prefix})
        if todays_entries:
            entry_len = len(todays_entries)
            todays_rep_no = entry_len
        else:
            todays_rep_no = 0
        new_entry_name = sr_name + sr_date + '.' + str(todays_rep_no)
                
        decontaminate_rec.write({'name' : new_entry_name, 'state' : 'confirm', 'report_confirm_date' : datetime.now(), 'user_id': self.env.user.id})
    
 
    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state == 'confirm':
                raise UserError(_('You cant delete a Decontamination Report that is already confirmed'))
        return super(DecontaminationReport, self).unlink()
    
    @api.model
    def create(self, vals):
        vals['name'] = 'Pending Confirmation'
        res = super(DecontaminationReport, self).create(vals)
        if vals.get('decontamination_items_ids',  False):
            serial_numbers = [line.lot_id.name for line in res.decontamination_items_ids]
            res.message_post(body=_('<ul class="o_mail_thread_message_tracking"><li> Serial Numbers: %s added. </li></ul>') % (','.join(map(str, serial_numbers)),))
        return res
    
    
    @api.multi
    def write(self, vals):
        if vals.get('decontamination_items_ids',  False):
            data = ''
            new_serial = []
            delete_serial = []
            changed = ''
            serial_head = '<ul class="o_mail_thread_message_tracking">'
            for line in vals['decontamination_items_ids']:
                if line[0] == 0:
                    new_serial_obj = self.env['stock.production.lot'].browse(line[2]['lot_id'])
                    new_serial.append(new_serial_obj.name)
                elif line[0] == 1:
                    line_obj = self.mapped('decontamination_items_ids').filtered(lambda x: x.id == line[1])
                    new_serial_obj = self.env['stock.production.lot'].browse(line[2]['lot_id'])
                    changed += """
                        <li>  Serial Number: <span>%s </span>
                        <span aria-label="Changed" class="fa fa-long-arrow-right" role="img" title="Changed"></span>
                        <span>%s </span>
                        </li>"""% (line_obj.lot_id.name,new_serial_obj.name)
                elif line[0] == 2:
                    line_obj = self.mapped('decontamination_items_ids').filtered(lambda x: x.id == line[1])
                    delete_serial.append(line_obj.lot_id.name)
            if new_serial:
                data += ('<li> Serial Numbers: %s Added. </li>') % (','.join(map(str, new_serial)),)
            if changed:
                data += changed
            if delete_serial:
                data += ('<li> Serial Numbers: %s Deleted. </li>') % (','.join(map(str, delete_serial)),)
            if data:
                self.message_post(body=_(serial_head + data + '</ul>'))
        res = super(DecontaminationReport, self).write(vals)
        return res


class DecontaminationReportLine(models.Model):
    _name = 'decontamination.report.line'
    _description = 'Decontamination Report Line'
    _rec_name = 'product_id'
    

    decontamination_id = fields.Many2one('decontamination.report', string='Decontamination ID', readonly=True)
    product_id = fields.Many2one('product.product', string="Product", store=True)
    default_code = fields.Char(string='Internal Reference')
    lot_id = fields.Many2one('stock.production.lot', string="Serial Number")
    
    
    @api.onchange('lot_id')
    def onchange_lot_id(self):
        if not self.lot_id:
            self.update({
                'product_id': False,
                'default_code': ''
            })
            return
        prodlot_obj = self.lot_id
        if prodlot_obj.product_id:
            self.update({
                'product_id':prodlot_obj.product_id.id,
                'default_code': prodlot_obj.product_id.default_code
                }) 
    
    @api.multi
    def unlink(self):
        for line in self:
            if line.decontamination_id and line.decontamination_id.state == 'confirm':
                raise UserError(_('You cant delete a line from Decontamination Report that is already confirmed'))
        return super(DecontaminationReportLine, self).unlink()
    