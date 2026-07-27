from src.dashboard.utils.db import *

print("Companies:", len(get_companies()))

print("Ratios:", len(get_ratios("INFY")))

print("Profit Loss:", len(get_pl("INFY")))

print("Balance Sheet:", len(get_bs("INFY")))

print("Cash Flow:", len(get_cf("INFY")))

print("Sectors:", len(get_sectors()))

print("Peers:", len(get_peers("IT Services")))

print("Valuation:", len(get_valuation("INFY")))