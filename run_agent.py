from scamguard.agent import investigate

sample = """URGENT! Your bank account will be blocked today.\nComplete KYC immediately and verify your OTP:\nhttps://secure-sbi-kyc-verification.com/login"""

result = investigate(sample, enable_reputation=False)
print(result["agent_report"])
