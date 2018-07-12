# This file reads in all of the datasets and saves them accordingly.
ctax_data_path = 'brc_data/'
btax_data_path = 'btax_data/'
gfactors = pd.read_csv('gfactors.csv')
historical_taxdata = pd.read_csv('historical_taxdata.csv')
# import tax revenue data
taxrev_data = pd.read_csv(ctax_data_path + 'taxrev.csv')
# import data for AMT model
amtdata2 = pd.read_csv(ctax_data_path + 'amt data2.csv')
# import data for FTC model
ftc_taxrates_data = pd.read_csv(ctax_data_path + 'ftc taxrates data.csv')
ftc_gdp_data = pd.read_csv(ctax_data_path + 'ftc gdp data.csv')
ftc_other_data = pd.read_csv(ctax_data_path + 'ftc other data.csv')
# import data for Sec. 199
sec199_data = pd.read_csv(ctax_data_path + 'sec199.csv')
# import depreciation data
df_econdepr = pd.read_csv(btax_data_path + 'Economic Depreciation Rates.csv')
asset = np.asarray(df_econdepr['Asset'])
asset[78] = 'Communications equipment manufacturing'
asset[81] = 'Motor vehicles and parts manufacturing'
df_econdepr['Asset'] = asset
df_econdepr.drop('Code', axis=1, inplace=True)
df_econdepr.rename(columns={'Economic Depreciation Rate': 'delta'},
                   inplace=True)
df_econdepr.drop([56, 89, 90], axis=0, inplace=True)
df_econdepr.reset_index(drop=True, inplace=True)
# import other data
investmentrate_data = pd.read_csv(ctax_data_path + 'investmentrates.csv')
investmentshare_data = pd.read_csv(ctax_data_path + 'investmentshares.csv')
investmentGfactors_data = pd.read_csv(ctax_data_path +
                                      'investment_gfactors.csv')
depreciationIRS_data = pd.read_csv(ctax_data_path + 'dep data.csv')
bonus_data = pd.read_csv(ctax_data_path + 'bonus_data.csv')
# import debt data
debt_data_corp = pd.read_csv(ctax_data_path + 'Corp debt data.csv')
debt_data_noncorp = pd.read_csv(ctax_data_path + 'Noncorp debt data.csv')
# import pass-through IRS data
partner_data = pd.read_csv(ctax_data_path + 'partnership data.csv')
Scorp_data = pd.read_csv(ctax_data_path + 'Scorp data.csv')
sp_data = pd.read_csv(ctax_data_path + 'sp_nonfarm data.csv')
# tax depreciation information
taxdep1 = pd.read_csv(btax_data_path + 'tax_depreciation_rates.csv')
taxdep1.drop(['System'], axis=1, inplace=True)
taxdep1.rename(columns={'GDS Life': 'L_gds', 'ADS Life': 'L_ads',
                        'Asset Type': 'Asset'}, inplace=True)
asset = np.asarray(taxdep1['Asset'])
asset[81] = 'Motor vehicles and parts manufacturing'
method = np.asarray(taxdep1['Method'])
method[asset == 'Land'] = 'None'
method[asset == 'Inventories'] = 'None'
taxdep1['Asset'] = asset
taxdep1['Method'] = method
taxdep1.drop([56, 89, 90], axis=0, inplace=True)
taxdep1.reset_index(drop=True, inplace=True)
taxdep_info_gross = taxdep1.merge(right=df_econdepr, how='outer', on='Asset')
btax_defaults = pd.read_csv('mini_params_btax.csv')
econ_defaults = pd.read_csv('mini_params_econ.csv')
assets_data = pd.read_csv('mini_assets.csv')
assets_data.drop([3, 21, 32, 91], axis=0, inplace=True)
assets_data.reset_index(drop=True, inplace=True)
# Rescaling factors for later
rescale_corp = np.ones(14)
rescale_noncorp = np.ones(14)
if track_progress:
    print("Data imports complete")
