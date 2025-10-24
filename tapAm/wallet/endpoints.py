monifyApi = 'https://sandbox.monnify.com/api/v1'
monifyApiV2 = 'https://sandbox.monnify.com/api/v2'


disbursement = f'{monifyApi}/disbursements'
disbursementV2 = f'{monifyApiV2}/disbursements'

wallet = f'{disbursement}/wallet'
auth = f'{monifyApi}/auth'
walletBalance = f'{wallet}/balance'
walletTransactions = f'{wallet}/transactions'
# https://sandbox.monnify.com/api/v2/disbursements/single

singleTransfer = f'{monifyApiV2}/disbursements/single'
authToken = f'{auth}/login'
singleOTPValidation = f'{singleTransfer}/validate-otp'
# https://sandbox.monnify.com/api/v2/disbursements/single/validate-otp



# curl -H "Accept: application/json"
# https://sandbox.monnify.com/api/v1/disbursements/wallet/8016472829/statement
# ?startDate=1702076400000&endDate=1702458365000&enableTimeFilter=true&pageNo=
# 0&pageSize=11
