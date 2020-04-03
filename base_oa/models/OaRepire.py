# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class OaRepire():
    _name = 'oa.repire'
    """
    资产维修流程
    """
    _inherit = ['oa.base']

    name = fields.Char("Name")
    model = fields.Char("Model")
    code = fields.Char("Code")
    date = fields.Datetime("Date")
    owner_employee_id = fields.Many2one("hr.employee", "owner_employee_id")


    @api.depends()
    def _build_oa_repire(self):
        return ()

for record in records:
    for l in record.line_ids:
        if l.account_id.user_type_id.id == 3:

            for line in record.line_ids:
                # 销售产成品、商品、提供劳务收到的现金
                if line.account_id.code in ['1121000', '1122000', '1406000', '2203000', '6001000', '6041000', '6051000',
                                            '6051002']:
                    line.write({'analytic_tag_ids': [(4, 18)]})
                # 收到其他与经营活动有关的现金
                if line.account_id.code in ['2002000', '6021000', '6301000', '6301001', '6301002', '6301003', '6301004',
                                            '6301005']:
                    line.write({'analytic_tag_ids': [(4, 19)]})
                # 购买原材料、商品、接受劳务支付的现金
                if line.account_id.code in ['1122300', '1122500', '1123000', '1400100', '1400400', '1400500', '1401000',
                                            '1402000',
                                            '1403000', '1404000', '1405000', '1407000', '1408000', '1411000', '1411001',
                                            '1411002',
                                            '1411003', '2201000', '2202000', '2202020', '6051001', '6401000', '6402000'
                                            ]:
                    line.write({'analytic_tag_ids': [(4, 20)]})
                # 支付给职工以及为职工支付的现金
                if line.account_id.code == '2211000':
                    line.write({'analytic_tag_ids': [(4, 21)]})
                # 支付的税费
                if '6403' in line.account_id.code or line.account_id.code in ['2221000', '2221020', '2221021']:
                    line.write({'analytic_tag_ids': [(4, 22)]})
                # 支付其他与经营活动有关的现金
                if '1421' in line.account_id.code or '1801' in line.account_id.code or '5101' in line.account_id.code or '6601' in line.account_id.code \
                        or '6602' in line.account_id.code or '6603' in line.account_id.code and '6603003' not in line.account_id.code or '6605' in line.account_id.code \
                        or '6606' in line.account_id.code or '6711' in line.account_id.code \
                        or line.account_id.code in ['1031000', '1811000', '5001000', '5201000',
                                                    '5301000', '5401000', '5402000', '5403000', '6411000', '6421000',
                                                    '6501000',
                                                    '6502000', '6511000', '6521000',
                                                    '6531000', '6541000', '6542000', '6604000', '6701000', '6701100',
                                                    '6801000',
                                                    '6901000']:
                    line.write({'analytic_tag_ids': [(4, 23)]})
                    # 公司间相互代收款/付款/转款
                if line.account_id.code in ['1011000', '1011001', '1011002', '1011003', '1012000', '2001001',
                                            '2012000']:
                    line.write({'analytic_tag_ids': [(4, 34)]})
                # 处置固定资产、无形资产收回的现金净额
                if line.account_id.code == '1606000':
                    line.write({'analytic_tag_ids': [(4, 24)]})
                # 取得投资收益收到的现金
                if line.account_id.code in ['1131000', '1132000', '6011000', '6111000']:
                    line.write({'analytic_tag_ids': [(4, 26)]})
                # 构建固定资产和无形资产支付的现金
                if line.account_id.code in ['1601000', '1604000', '1605000', '1701000', '1711000']:
                    line.write({'analytic_tag_ids': [(4, 27)]})
                # 短期投资、长期债券和长期股权投资支付的现金
                if line.account_id.code in ['1501000', '1503000']:
                    line.write({'analytic_tag_ids': [(4, 28)]})
                    # 支付其他与投资活动有关的现金
                if line.account_id.code == '2231000':
                    line.write({'analytic_tag_ids': [(4, 33)]})
                # 吸收投资者投资收到的现金
                if line.account_id.code == '4001000':
                    line.write({'analytic_tag_ids': [(4, 30)]})
                # 分配利润支付的现金
                if line.account_id.code in ['2232000', '4103000', '4104000', '999999']:
                    line.write({'analytic_tag_ids': [(4, 32)]})
                # 特殊科目处理（1221000,1221001,1531000,2241000,2701000）
                if line.account_id.code in ['1221000', '1221001', '1531000', '2241000', '2701000']:
                    if line.debit == 0:
                        line.write({'analytic_tag_ids': [(4, 19)]})
                    else:
                        line.write({'analytic_tag_ids': [(4, 23)]})
                # 特殊科目处理（2001000, 2501000）
                if line.account_id.code in ['2001000', '2501000']:
                    if line.credit == 0:
                        line.write({'analytic_tag_ids': [(4, 31)]})
                    else:
                        line.write({'analytic_tag_ids': [(4, 29)]})
                        # 特殊科目处理（1511000）
                if line.account_id.code == '1511000':
                    if line.debit == 0:
                        line.write({'analytic_tag_ids': [(4, 25)]})
                    else:
                        line.write({'analytic_tag_ids': [(4, 28)]})

                    #break
