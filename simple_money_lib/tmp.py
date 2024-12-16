# Currency.register(
#         code="BTC_8",
#         numeric=None,  # Assuming no numeric code for BTC_8
#         sub_unit=8,    # Custom sub-unit for BTC_8
#         name="Bitcoin (8 decimals)"
#     )
#
# for item in Currency.all_currencies():
#     print(item)

from simple_money_lib.parsers.simple_parser import SimpleMoneyParser

mp = SimpleMoneyParser()
res = []
cases = ["100 BTC_8", "BTC_8 100", "BTC_8100"]
for case in cases:
    res.append(mp.parse(case))

print("HMM", res)

