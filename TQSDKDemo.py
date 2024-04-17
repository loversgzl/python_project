from tqsdk import TqApi, TqAccount, TqAuth, TqKq



def quote_list():
    api = TqApi(auth=TqAuth("快期账户", "账户密码"), debug=False)
    quote_list = api.get_quote_list(["SHFE.cu2105", "SHFE.cu2112"])
    print(quote_list[0].last_price, quote_list[1].last_price)
    while api.wait_update():
        print(quote_list[0].last_price, quote_list[1].last_price)



if __name__ == '__main__':
    print("")

