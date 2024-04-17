from tqsdk import TqApi, TqAccount, TqAuth, TqKq

def check_symbol():
    SHFE_symbol_list = ['SHFE.ss2401','SHFE.ss2402','SHFE.ss2403','SHFE.ss2404','SHFE.ss2405','SHFE.ss2406','SHFE.ss2407','SHFE.ss2408','SHFE.ss2409','SHFE.ss2410','SHFE.ss2411','SHFE.ss2412',
                        'SHFE.rb2401','SHFE.rb2402','SHFE.rb2403','SHFE.rb2404','SHFE.rb2405','SHFE.rb2406','SHFE.rb2407','SHFE.rb2408','SHFE.rb2409','SHFE.rb2410','SHFE.rb2411','SHFE.rb2412',
                        'SHFE.hc2401','SHFE.hc2402','SHFE.hc2403','SHFE.hc2404','SHFE.hc2405','SHFE.hc2406','SHFE.hc2407','SHFE.hc2408','SHFE.hc2409','SHFE.hc2410','SHFE.hc2411','SHFE.hc2412',
                        'SHFE.wr2401','SHFE.wr2402','SHFE.wr2403','SHFE.wr2404','SHFE.wr2405','SHFE.wr2406','SHFE.wr2407','SHFE.wr2408','SHFE.wr2409','SHFE.wr2410','SHFE.wr2411','SHFE.wr2412',
                        'SHFE.au2401','SHFE.au2402','SHFE.au2403','SHFE.au2404','SHFE.au2405','SHFE.au2406','SHFE.au2407','SHFE.au2408','SHFE.au2409','SHFE.au2410','SHFE.au2411','SHFE.au2412',
                        'SHFE.ag2401','SHFE.ag2402','SHFE.ag2403','SHFE.ag2404','SHFE.ag2405','SHFE.ag2406','SHFE.ag2407','SHFE.ag2408','SHFE.ag2409','SHFE.ag2410','SHFE.ag2411','SHFE.ag2412',
                        'SHFE.cu2401','SHFE.cu2402','SHFE.cu2403','SHFE.cu2404','SHFE.cu2405','SHFE.cu2406','SHFE.cu2407','SHFE.cu2408','SHFE.cu2409','SHFE.cu2410','SHFE.cu2411','SHFE.cu2412',
                        'SHFE.sp2401','SHFE.sp2402','SHFE.sp2403','SHFE.sp2404','SHFE.sp2405','SHFE.sp2406','SHFE.sp2407','SHFE.sp2408','SHFE.sp2409','SHFE.sp2410','SHFE.sp2411','SHFE.sp2412',
                        'SHFE.bu2401','SHFE.bu2402','SHFE.bu2403','SHFE.bu2404','SHFE.bu2405','SHFE.bu2406','SHFE.bu2407','SHFE.bu2408','SHFE.bu2409','SHFE.bu2410','SHFE.bu2411','SHFE.bu2412',
                        'SHFE.ru2401','SHFE.ru2402','SHFE.ru2403','SHFE.ru2404','SHFE.ru2405','SHFE.ru2406','SHFE.ru2407','SHFE.ru2408','SHFE.ru2409','SHFE.ru2410','SHFE.ru2411','SHFE.ru2412',
                        'SHFE.br2401','SHFE.br2402','SHFE.br2403','SHFE.br2404','SHFE.br2405','SHFE.br2406','SHFE.br2407','SHFE.br2408','SHFE.br2409','SHFE.br2410','SHFE.br2411','SHFE.br2412',
                        'SHFE.fu2401','SHFE.fu2402','SHFE.fu2403','SHFE.fu2404','SHFE.fu2405','SHFE.fu2406','SHFE.fu2407','SHFE.fu2408','SHFE.fu2409','SHFE.fu2410','SHFE.fu2411','SHFE.fu2412',
                        'SHFE.zn2401','SHFE.zn2402','SHFE.zn2403','SHFE.zn2404','SHFE.zn2405','SHFE.zn2406','SHFE.zn2407','SHFE.zn2408','SHFE.zn2409','SHFE.zn2410','SHFE.zn2411','SHFE.zn2412',
                        'SHFE.pb2401','SHFE.pb2402','SHFE.pb2403','SHFE.pb2404','SHFE.pb2405','SHFE.pb2406','SHFE.pb2407','SHFE.pb2408','SHFE.pb2409','SHFE.pb2410','SHFE.pb2411','SHFE.pb2412',
                        'SHFE.sn2401','SHFE.sn2402','SHFE.sn2403','SHFE.sn2404','SHFE.sn2405','SHFE.sn2406','SHFE.sn2407','SHFE.sn2408','SHFE.sn2409','SHFE.sn2410','SHFE.sn2411','SHFE.sn2412',
                        'SHFE.ni2401','SHFE.ni2402','SHFE.ni2403','SHFE.ni2404','SHFE.ni2405','SHFE.ni2406','SHFE.ni2407','SHFE.ni2408','SHFE.ni2409','SHFE.ni2410','SHFE.ni2411','SHFE.ni2412',
                        'SHFE.al2401','SHFE.al2402','SHFE.al2403','SHFE.al2404','SHFE.al2405','SHFE.al2406','SHFE.al2407','SHFE.al2408','SHFE.al2409','SHFE.al2410','SHFE.al2411','SHFE.al2412',
                        'SHFE.ao2401','SHFE.ao2402','SHFE.ao2403','SHFE.ao2404','SHFE.ao2405','SHFE.ao2406','SHFE.ao2407','SHFE.ao2408','SHFE.ao2409','SHFE.ao2410','SHFE.ao2411','SHFE.ao2412']
    DCE_symbol_list = ['DCE.pp2401', 'DCE.eb2401', 'DCE.v2401', 'DCE.l2401', 'DCE.eg2401', 'DCE.pg2401', 'DCE.a2401', 'DCE.b2401', 'DCE.m2401', 'DCE.c2401', 'DCE.cs2401', 'DCE.rr2401',
                       'DCE.lh2401', 'DCE.jd2401', 'DCE.y2401', 'DCE.p2401', 'DCE.i2401', 'DCE.j2401', 'DCE.fb2401', 'DCE.bb2401']
    CZCE_symbol_ist = ['CZCE.PM401', 'CZCE.RI401', 'CZCE.LR401', 'CZCE.JR401', 'CZCE.RS401', 'CZCE.OI401', 'CZCE.RM401', 'CZCE.WH401', 'CZCE.CF401', 'CZCE.CY401', 'CZCE.PF401',
                        'CZCE.CJ401', 'CZCE.AP401', 'CZCE.SR401', 'CZCE.PK401', 'CZCE.UR401', 'CZCE.SA401', 'CZCE.SH401', 'CZCE.PX401', 'CZCE.TA401', 'CZCE.MA401', 'CZCE.FG401',
                        'CZCE.ZC401', 'CZCE.SM401', 'CZCE.SF401']
    GFEX_symbol_list = ['GFEX.si2401', 'GFEX.lc2401']
    INE_symbol_list = ['INE.sc2401', 'INE.nr2401', 'INE.bc2401', 'INE.lu2401', 'INE.ec2401']
    # symbolList = ["CZCE.RS407", "CZCE.SH401", "CZCE.PX401", "INE.ec2401"]
    symbolList = ["SHFE.au2407", "SHFE.au2307", "SHFE.au2207", "SHFE.au2107",]
    # symbolList.extend(SHFE_symbol_list)
    # symbolList.extend(DCE_symbol_list)
    # symbolList.extend(CZCE_symbol_ist)
    # symbolList.extend(GFEX_symbol_list)
    # symbolList.extend(INE_symbol_list)
    api = TqApi(auth=TqAuth("15088546658", "ivy123456"))
    for symbol in symbolList:
        try:
            api.get_quote(symbol)
            print("合约：%s, 检查成功"% symbol)
        except Exception as e:
            print("合约：%s, 检查失败"% symbol)
            api.close()
            api = TqApi(auth=TqAuth("15088546658", "ivy123456"))
    api.close()

if __name__ == '__main__':
    check_symbol()