"""
This file prepares the data for use by the Asset class.
It begins with the detailed asset types by industry from the BEA. 


"""

import numpy as np
import pandas as pd
import copy
import os
from biztax.data import Data
from biztax.asset import Asset
from biztax.policy import Policy
from biztax.years import START_YEAR, HISTORY_START

RAW_DATA_PATH = 'data_prep/historical_bea/'
OUTPUT_PATH = 'biztax/brc_data/'

# Import Excel files
stockfile = pd.ExcelFile(os.path.join(RAW_DATA_PATH, 'detailnonres_stk.xlsx'))
invfile = pd.ExcelFile(os.path.join(RAW_DATA_PATH, 'detailnonres_inv.xlsx'))
resfile = pd.ExcelFile(os.path.join(RAW_DATA_PATH, 'detailresidential.xlsx'))
firminvfile = pd.ExcelFile(os.path.join(RAW_DATA_PATH, 'nonres_firm_inv.xls'))
firmstkfile = pd.ExcelFile(os.path.join(RAW_DATA_PATH, 'nonres_firm_stk.xls'))

"""
SECTION 1. READING IN DATA ON PRIVATE NONRESIDENTIAL CAPITAL

Due to the structure of the file, each industry must be read in individually,
and then aggregated. The 
    Agriculture, forestry, fishing, and hunting:
        Farms (110C)
        Forestry, fishing, and related activities (113F)
    Mining:
        Oil and gas extraction (2110)
        Mining, except oil and gas (2120)
        Support activities for mining (2130)
    Utilities (2200)
    Construction (2300)
    Durable goods manufacturing:
        Wood products (3210)
        Nonmetallic mineral products (3270)
        Primary metals (3310)
        Fabricated metal products (3320)
        Machinery (3330)
        Computer and electronic products (3340)
        Electrical equipment, appliances, and components (3350)
        Motor vehicles, bodies and trailers, and parts (336M)
        Other transportation equipment (336O)
        Furniture and related products (3370)
        Miscellaneous manufacturing (338A)
    Nondurable goods manufacturing:
        Food, beverage, and tobacco products (311A)
        Textile mills and textile product mills (313T)
        Apparel and leather and allied products (315A)
        Paper products (3220)
        Printing and related support activities (3230)
        Petroleum and coal products (3240)
        Chemical products (3250)
        Plastics and rubber products (3260)
    Wholesaletrade (4200)
    Retailtrade (44RT)
    Transportation and warehousing:
        Air transportation (4810)
        Railroad transportation (4820)
        Water transportation (4830)
        Truck transportation (4840)
        Transit and ground passenger transportation (4850)
        Pipeline transportation (4860)
        Other transportation and support activities (487S)
        Warehousing and storage (4930)
    Information:
        Publishing industries (including software) (5110)
        Motion picture and sound recording industries (5120)
        Broadcasting and telecommunications (5130)
        Information and data processing services (5140)
    Finance and insurance:
        Federal Reserve banks (5210)
        Credit intermediation and related activities (5220)
        Securities, commodity contracts, and investments (5230)
        Insurance carriers and related activities (5240)
        Funds, trusts, and other financial vehicles (5250)
    Real estate and rental and leasing:
        Real estate (5310)
        Rental and leasing services and lessors of intangible assets (5320)
    Professional, scientific, and technical services:
        Legal services (5411)
        Computer systems design and related services (5415)
        Miscellaneous professional, scientific, and technical services (5412)
    Management of companies and enterprises (5500)
    Administrative and waste management services:
        Administrative and support services (5610)
        Waste management and remediation services (5620)
    Educational services (6100)
    Health care and social assistance:
        Ambulatory health care services (6210)
        Hospitals (622H)
        Nursing and residential care facilities (6230)
        Social assistance (6240)
    Arts, entertainment, and recreation:
        Performing arts, spectator sports, museums, and related activities (711A)
        Amusements, gambling, and recreation industries (7130)
    Accommodation and foodservices:
        Accommodation (7210)
        Food services and drinking places (7220)
    Other services, except government (8100)
We exclude following industries:
    Federal Reserve banks (5210)
    Funds, trusts, and other financial vehicles (5250)
We remove the following asset types:
    Household furniture
    Household appliances
    Religious structures
    Private universities and colleges
    Other nonprofit institutions
    
"""

def read_and_clean(ind, data):
    """
    Reads the relevant asset by industry data from the Excel files.
    Parameters:
        ind: String for the BEA industry code
        data: String for asset stock ('stock') or investment ('inv')
    Returns a DataFrame
    """
    if data == 'inv':
        data1 = pd.read_excel(invfile, sheet_name=ind, header=5)
    elif data == 'stock':
        data1 = pd.read_excel(stockfile, sheet_name=ind, header=5)
    else:
        raise ValueError('Data file must be inv or stock')
    # Drop empty row and aggregate rows
    data1.drop([0, 1, 41, 74], axis=0, inplace=True)
    # Drop unwanted asset types
    data1.drop([30, 38, 59, 93, 94], axis=0, inplace=True)
    syr = 1901 if data=='inv' else 1947
    data1.drop(map(str, range(syr, HISTORY_START)), axis=1, inplace=True)
    data1.drop(map(str, range(START_YEAR + 1, 2018)), axis=1, inplace=True)
    data1.rename({'NIPA Asset Types': 'asset_name',
                  'Asset Codes': 'asset_code'}, axis=1, inplace=True)
    data1.set_index('asset_code', inplace=True)
    return data1

ind_codes = ['110C', '113F', '2110', '2120', '2130', '2200', '2300', '3210',
             '3270', '3310', '3320', '3330', '3340', '3350', '336M', '336O',
             '3370', '338A', '311A', '313T', '315A', '3220', '3230', '3240',
             '3250', '3260', '4200', '44RT', '4810', '4820', '4830', '4840',
             '4850', '4860', '487S', '4930', '5110', '5120', '5130', '5140',
             '5220', '5230', '5240', '5310', '5320', '5411', '5415', '5412',
             '5500', '5610', '5620', '6100', '6210', '622H', '6230', '6240',
             '711A', '7130', '7210', '7220', '8100']
industries = ['ALL', 'FARM', 'FFRA', 'MINE', 'UTIL', 'CNST',
              'DMAN', 'NMAN', 'WHTR', 'RETR', 'TRAN', 'INFO',
              'FINC', 'FINS', 'INSU', 'REAL', 'LEAS', 'PROF',
              'MGMT', 'ADMN', 'EDUC', 'HLTH', 'ARTS', 'ACCM', 'OTHS']
ind_dict = {'ALL': ind_codes,
            'FARM': ['110C'],
            'FFRA': ['113F'],
            'MINE': ['2110', '2120', '2130'],
            'UTIL': ['2200'],
            'CNST': ['2300'],
            'DMAN': ['3210', '3270', '3310', '3320', '3330', '3340', '3350',
                     '336M', '336O', '3370', '338A'],
            'NMAN': ['311A', '313T', '315A', '3220', '3230', '3240',
                     '3250', '3260'],
            'WHTR': ['4200'],
            'RETR': ['44RT'],
            'TRAN': ['4810', '4820', '4830', '4840', '4850', '4860', '487S', '4930'],
            'INFO': ['5110', '5120', '5130', '5140'],
            'FINC': ['5220'],
            'FINS': ['5230'],
            'INSU': ['5240'],
            'REAL': ['5310'],
            'LEAS': ['5320'],
            'PROF': ['5411', '5415', '5412'],
            'MGMT': ['5500'],
            'ADMN': ['5610', '5620'],
            'EDUC': ['6100'],
            'HLTH': ['6210', '622H', '6230', '6240'],
            'ARTS': ['711A', '7130'],
            'ACCM': ['7210', '7220'],
            'OTHS': ['8100']}
cleaned_data = dict()
for ind in ind_codes:
    newdf1 = read_and_clean(ind, 'inv')
    newdf1.drop(['asset_name'], axis=1, inplace=True)
    newdf2 = read_and_clean(ind, 'stock')
    newdf2.drop(['asset_name'], axis=1, inplace=True)
    cleaned_data['nresinv_' + ind] = newdf1
    cleaned_data['nresstk_' + ind] = newdf2


"""
SECTION 2. RENTAL RESIDENTIAL CAPITAL

This section reads in data on residential capital. We restrict it to the
corporate category and the sole proprietorships and partnerships category.
All of these are for tenant-occupied residential capital, aka rental
residential capital. We then group the various categories as follows, and we
give them codes.
    Rental residential, new (RR10)
    Rental residential, additions and alterations (RR20)
    Rental residential, major improvements (RR30)
    Rental residential, equipment (RR40)
"""
# Rental residential investment
resinv = pd.read_excel(resfile, sheet_name='Investment ', header=5)
resinv.drop(map(str, range(1901, HISTORY_START)), axis=1, inplace=True)
resinv.drop(map(str, range(START_YEAR + 1, 2018)), axis=1, inplace=True)
resinv.drop(['Asset Codes', 'Unnamed: 1'], axis=1, inplace=True)
# Corporate rental residential, new investment
rr10_c_inv = np.array(resinv.iloc[24] + resinv.iloc[27])
# Corporate rental residential, additions and alterations
rr20_c_inv = np.array(resinv.iloc[25] + resinv.iloc[28])
# Corporate rental residential, major improvements
rr30_c_inv = np.array(resinv.iloc[26] + resinv.iloc[29])
# Corporate rental residential, equipment
rr40_c_inv = np.array(resinv.iloc[32] + resinv.iloc[33])
# Sole proprietorship and partnership rental residential, new investment
rr10_nc_inv = np.array(resinv.iloc[36] + resinv.iloc[39] + resinv.iloc[42])
# Sole proprietorship and partnership rental residential, additions/alterations
rr20_nc_inv = np.array(resinv.iloc[37] + resinv.iloc[40])
# Sole proprietorship and partnership rental residential, major improvements
rr30_nc_inv = np.array(resinv.iloc[38] + resinv.iloc[41])
# Sole proprietorship and partnership rental residential, equipment
rr40_nc_inv = np.array(resinv.iloc[45] + resinv.iloc[46])

# Rental residential capital stock
resstk = pd.read_excel(resfile, sheet_name='Net Stock (Current-Cost)', header=5)
resstk.drop(map(str, range(1925, HISTORY_START)), axis=1, inplace=True)
resstk.drop(map(str, range(START_YEAR + 1, 2018)), axis=1, inplace=True)
resstk.drop(['Asset Codes', 'Unnamed: 1'], axis=1, inplace=True)
# Corporate rental residential, building stock
rr10_c_stk = np.array(resstk.iloc[24] + resstk.iloc[27])
# Corporate rental residential, accumulated additions and alterations
rr20_c_stk = np.array(resstk.iloc[25] + resstk.iloc[28])
# Corporate rental residential, accumulated major improvements
rr30_c_stk = np.array(resstk.iloc[26] + resstk.iloc[29])
# Corporate rental residential, equipment
rr40_c_stk = np.array(resstk.iloc[32] + resstk.iloc[33])
# Sole proprietorship and partnership rental residential, building stock
rr10_nc_stk = np.array(resstk.iloc[36] + resstk.iloc[39] + resstk.iloc[42])
# Sole proprietorship and partnership rental residential, accumulated additions/alterations
rr20_nc_stk = np.array(resstk.iloc[37] + resstk.iloc[40])
# Sole proprietorship and partnership rental residential, accumulated major improvements
rr30_nc_stk = np.array(resstk.iloc[38] + resstk.iloc[41])
# Sole proprietorship and partnership rental residential, equipment
rr40_nc_stk = np.array(resstk.iloc[45] + resstk.iloc[46])


"""
SECTION 3. DATA FOR SPLITTING BY FIRM TYPE

This section uses data from BEA Fixed Asset tables 4.1 and 4.7 to split
historical investment and capital by legal form of organization, with different
splits for equipment, structures, and intellectual property. We compute the
shares of investment in each major asset type for corporations and for
noncorporate businesses in each year.
"""
# Read in investment by legal type and major category
firm_inv = pd.read_excel(firminvfile, sheet_name='Sheet0', header=5)
firm_inv.drop(map(str, range(1901, HISTORY_START)), axis=1, inplace=True)
firm_inv.drop(map(str, range(START_YEAR + 1, 2018)), axis=1, inplace=True)
firm_inv.drop(['Line', 'Unnamed: 1'], axis=1, inplace=True)
# Read in asset stock by legal type and major category
firm_stk = pd.read_excel(firmstkfile, sheet_name='Sheet0', header=5)
firm_stk.drop(map(str, range(1925, HISTORY_START)), axis=1, inplace=True)
firm_stk.drop(map(str, range(START_YEAR + 1, 2018)), axis=1, inplace=True)
firm_stk.drop(['Line', 'Unnamed: 1'], axis=1, inplace=True)
# Extract totals for major asset categories
inv_eq_tot = np.array(firm_inv.iloc[2])
inv_st_tot = np.array(firm_inv.iloc[3])
inv_ip_tot = np.array(firm_inv.iloc[4])
stk_eq_tot = np.array(firm_stk.iloc[2])
stk_st_tot = np.array(firm_stk.iloc[3])
stk_ip_tot = np.array(firm_stk.iloc[4])
# Extract shares for corporations
inv_eq_c = np.array(firm_inv.iloc[20]) / inv_eq_tot
inv_st_c = np.array(firm_inv.iloc[21]) / inv_st_tot
inv_ip_c = np.array(firm_inv.iloc[22]) / inv_ip_tot
stk_eq_c = np.array(firm_stk.iloc[20]) / stk_eq_tot
stk_st_c = np.array(firm_stk.iloc[21]) / stk_st_tot
stk_ip_c = np.array(firm_stk.iloc[22]) / stk_ip_tot
# Extract shares for noncorporate businesses
inv_eq_nc = np.array(firm_inv.iloc[64] + firm_inv.iloc[68]) / inv_eq_tot
inv_st_nc = np.array(firm_inv.iloc[65] + firm_inv.iloc[69]) / inv_st_tot
inv_ip_nc = np.array(firm_inv.iloc[66] + firm_inv.iloc[70]) / inv_ip_tot
stk_eq_nc = np.array(firm_stk.iloc[64] + firm_stk.iloc[68]) / stk_eq_tot
stk_st_nc = np.array(firm_stk.iloc[65] + firm_stk.iloc[69]) / stk_st_tot
stk_ip_nc = np.array(firm_stk.iloc[66] + firm_stk.iloc[70]) / stk_ip_tot

"""
SECTION 4. SEMI-FINAL DATASETS

This section uses all of the above work to produce the final datasets. It
splits takes the investment and capital DataFrames and multiplies each entry by
the relevant firm share for the major asset type and year. It then adds in the
rental residential amounts and saves the resulting DataFrames. This produces
the following DataFrames for use by the Asset object:
    investment_corp.csv
    investment_ncorp.csv
    capitalstock_corp.csv
    capitalstock.ncorp.csv
"""

def buildData(ind, corp):
    investment1 = cleaned_data['nresinv_' + ind_dict[ind][0]]
    capital1 = cleaned_data['nresstk_' + ind_dict[ind][0]]
    if len(ind_dict[ind]) > 1:
        for ind2 in ind_dict[ind][1:]:
            investment1 += cleaned_data['nresinv_' + ind2]
            capital1 += cleaned_data['nresstk_' + ind2]
    investment2 = investment1.transpose()
    capital2 = capital1.transpose()
    if corp:
        inv_eq = inv_eq_c
        inv_st = inv_st_c
        inv_ip = inv_ip_c
        stk_eq = stk_eq_c
        stk_st = stk_st_c
        stk_ip = stk_ip_c
    else:
        inv_eq = inv_eq_nc
        inv_st = inv_st_nc
        inv_ip = inv_ip_nc
        stk_eq = stk_eq_nc
        stk_st = stk_st_nc
        stk_ip = stk_ip_nc
    for code in list(investment2):
        if code[:2] in ['EP', 'EI', 'ET', 'EO']:
            # Use corporate share for equipment
            investment2[code] = investment2[code] * inv_eq
            capital2[code] = capital2[code] * stk_eq
        elif code[0] == 'S':
            # Use corporate share for structures
            investment2[code] = investment2[code] * inv_st
            capital2[code] = capital2[code] * stk_st
        elif code[:2] in ['EN', 'RD', 'AE']:
            # Use corporate share for intellectual property
            investment2[code] = investment2[code] * inv_ip
            capital2[code] = capital2[code] * stk_ip
        else:
            # Check for anything unaccounted for
            raise ValueError('unknown asset code: ' + code)
    if ind in ['ALL', 'REAL']:
        if corp:
            investment2['RR10'] = rr10_c_inv
            investment2['RR20'] = rr20_c_inv
            investment2['RR30'] = rr30_c_inv
            investment2['RR40'] = rr40_c_inv
            capital2['RR10'] = rr10_c_stk
            capital2['RR20'] = rr20_c_stk
            capital2['RR30'] = rr30_c_stk
            capital2['RR40'] = rr40_c_stk
        else:
            investment2['RR10'] = rr10_nc_inv
            investment2['RR20'] = rr20_nc_inv
            investment2['RR30'] = rr30_nc_inv
            investment2['RR40'] = rr40_nc_inv
            capital2['RR10'] = rr10_nc_stk
            capital2['RR20'] = rr20_nc_stk
            capital2['RR30'] = rr30_nc_stk
            capital2['RR40'] = rr40_nc_stk
    else:
        investment2['RR10'] = 0.
        investment2['RR20'] = 0.
        investment2['RR30'] = 0.
        investment2['RR40'] = 0.
        capital2['RR10'] = 0.
        capital2['RR20'] = 0.
        capital2['RR30'] = 0.
        capital2['RR40'] = 0.
    investment3 = investment2.transpose()
    capital3 = capital2.transpose()
    investment3['industry'] = ind
    capital3['industry'] = ind
    investment3.reset_index(inplace=True)
    capital3.reset_index(inplace=True)
    return (investment3, capital3)

(investment_corp, capital_corp) = buildData('ALL', True)
(investment_ncorp, capital_ncorp) = buildData('ALL', False)

for ind in industries[1:]:
    (invcorp, capcorp) = buildData(ind, True)
    (invncorp, capncorp) = buildData(ind, False)
    investment_corp = investment_corp.append(invcorp, ignore_index=True)
    investment_ncorp = investment_ncorp.append(invncorp, ignore_index=True)
    capital_corp = capital_corp.append(capcorp, ignore_index=True)
    capital_ncorp = capital_ncorp.append(capncorp, ignore_index=True)

investment_corp.to_csv(OUTPUT_PATH + 'investment_corp.csv', index=False)
investment_ncorp.to_csv(OUTPUT_PATH + 'investment_ncorp.csv', index=False)
capital_corp.to_csv(OUTPUT_PATH + 'capital_corp.csv', index=False)
capital_ncorp.to_csv(OUTPUT_PATH + 'capital_ncorp.csv', index=False)


"""
SECTION 4. CALIBRATING WITH THE DEPRECIATION MODEL

This section imports the Asset class and uses the data produced above to run
the depreciation model for 2000-2013. Once that model has been run, we
calculate a rescaling factor to match depreciation totals in the model. 
Note that depreciation totals exclude R&D and software, which are expensed
or amortized. The rescaling is also applied for these categories, although
future improvements would separate this. 
Once this is complete, we use these rescaling factors to adjust the investment
and capital tables for each firm type and save them. This process replaces the
use of adjustment factors for depreciation and capital in the current model.

NOTE: Switch to calculating different factors for each industry.
"""

def calcDepAdjustment(corp):
    """
    Calculates the adjustment factor for assets, depreciation and investment
    corp: indicator for whether corporate or noncorporate data
    """
    # Create Asset object
    policy = Policy()
    asset1 = Asset(policy.parameters_dataframe(), corp)
    asset1.calc_all()
    # Get unscaled depreciation for all years
    totalAnnualDepreciation = asset1.calcDep_allyears()
    # Get IRS data
    depreciation_data = copy.deepcopy(asset1.data.depreciationIRS_data)
    depreciation_data['dep_model'] = totalAnnualDepreciation[40:54]
    if corp:
        depreciation_data['scale'] = (depreciation_data['dep_Ccorp'] /
                                      depreciation_data['dep_model'])
    else:
        depreciation_data['scale'] = ((depreciation_data['dep_Scorp'] +
                                       depreciation_data['dep_sp'] +
                                       depreciation_data['dep_partner']) /
                                      depreciation_data['dep_model'])
    adj_factor = (sum(depreciation_data['scale']) /
                  len(depreciation_data['scale']))
    # depreciation_data.to_csv('depr_data_' + str(corp) + '.csv')
    return adj_factor

adjfactor_dep_corp = calcDepAdjustment(True)
adjfactor_dep_noncorp = calcDepAdjustment(False)
print('Corp adjustment factor: ' + str(adjfactor_dep_corp * 1000))
print('Noncorp adjustment factor: ' + str(adjfactor_dep_noncorp * 1000))

# Rescale the capital and investment datasets using adjustment factors
industry1 = investment_corp['industry']
assetcodes = investment_corp['asset_code']
investment_corp.drop(['industry', 'asset_code'], axis=1, inplace=True)
investment_ncorp.drop(['industry', 'asset_code'], axis=1, inplace=True)
capital_corp.drop(['industry', 'asset_code'], axis=1, inplace=True)
capital_ncorp.drop(['industry', 'asset_code'], axis=1, inplace=True)

investment_corp2 = investment_corp * adjfactor_dep_corp
capital_corp2 = capital_corp * adjfactor_dep_corp
investment_ncorp2 = investment_ncorp * adjfactor_dep_noncorp
capital_ncorp2 = capital_ncorp * adjfactor_dep_noncorp

investment_corp2['industry'] = industry1
investment_ncorp2['industry'] = industry1
capital_corp2['industry'] = industry1
capital_ncorp2['industry'] = industry1
investment_corp2['asset_code'] = assetcodes
investment_ncorp2['asset_code'] = assetcodes
capital_corp2['asset_code'] = assetcodes
capital_ncorp2['asset_code'] = assetcodes

investment_corp2.to_csv(OUTPUT_PATH + 'investment_corp.csv', index=False)
capital_corp2.to_csv(OUTPUT_PATH + 'capital_corp.csv', index=False)
investment_ncorp2.to_csv(OUTPUT_PATH + 'investment_ncorp.csv', index=False)
capital_ncorp2.to_csv(OUTPUT_PATH + 'capital_ncorp.csv', index=False)



