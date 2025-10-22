monifyApi = 'https://sandbox.monnify.com/api/v1'
monifyApiV2 = 'https://sandbox.monnify.com/api/v2'

disbursement = f'{monifyApi}/disbursements'
wallet = f'{disbursement}/wallet'
auth = f'{monifyApi}/auth'
walletBalance = f'{wallet}/balance'
walletTransactions = f'{wallet}/transactions'
# https://sandbox.monnify.com/api/v2/disbursements/single
singleTransfer = f'{monifyApiV2}/disbursements/single'
authToken = f'{auth}/login'



# curl -H "Accept: application/json"
# https://sandbox.monnify.com/api/v1/disbursements/wallet/8016472829/statement
# ?startDate=1702076400000&endDate=1702458365000&enableTimeFilter=true&pageNo=
# 0&pageSize=11
