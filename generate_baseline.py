"""
The code in this file calculates and saves the various adjustment factors
and DataFrames necessary for the calculations in Business-Taxation.

We need to produce the following objects:
    adjfactors.csv
    pass-through shares
"""
import copy
import numpy as np
import pandas as pd
import scipy.optimize
from biztax.data import Data
from biztax.asset import Asset
from biztax.debt import Debt
from biztax.policy import Policy



# Specify single Data object (for convenience)
data1 = Data()


"""
Section 1. Calculation of the adjustment parameters
"""


def calcAMTparams2():
    """
    Calculates the adjustment factors for the AMT and PYMTC
    """
    # Grab historical data
    hist_data = copy.deepcopy(data1.historical_combined)
    taxinc = np.array(hist_data['taxinc'])
    amt = np.array(hist_data['amt'])
    stock13 = 26.0
    A13 = 4.196871
    tau_a = 0.2
    tau_c = 0.347
    pi0 = 0.865
    pi1 = 0.494
    gamma = (A13 * (2. - pi0 - pi1) /
             (stock13 * (1. - pi1) + A13 * (1. - pi0 - pi1)))
    A_over_TI = sum([amt[i] / taxinc[i] for i in range(16)]) / 16.
    # Calculate solution to AMT parameter

    def amterr(lam):
        # Squared difference between actual AMT/TaxInc ratio vs. predicted
        ATI_pred = tau_a / lam * np.exp(-lam * (tau_c / tau_a - 1))
        err = (ATI_pred - A_over_TI)**2
        return err

    lamf = scipy.optimize.minimize_scalar(amterr,
                                          bounds=(0.001, 100),
                                          method='bounded').x
    theta = np.exp(-lamf * (tau_c / tau_a - 1))
    return (lamf, theta, gamma, pi1, pi0)


def calcWAvgTaxRate(year):
    """
    Calculates the weighted average statutory corporate tax rate
    in all OECD countries in a given year.
    """
    assert year in range(1995, 2028)
    year = min(year, 2016)
    gdp_list = np.asarray(data1.ftc_gdp_data[str(year)])
    taxrate_list = np.asarray(data1.ftc_taxrates_data[str(year)])
    # remove observations with missing data
    taxrate_list2 = np.where(np.isnan(taxrate_list), 0, taxrate_list)
    gdp_list2 = np.where(np.isnan(taxrate_list), 0, gdp_list)
    avgrate = sum(taxrate_list2 * gdp_list2) / sum(gdp_list2)
    return avgrate


def calcFTCAdjustment():
    """
    Calculates the adjustment factor for the FTC.
    """
    ftc_actual = np.asarray(data1.ftc_other_data['F'][:19])
    profits = np.asarray(data1.ftc_other_data['C_total'][:19])
    profits_d = np.asarray(data1.ftc_other_data['C_domestic'][:19])
    profits_f = profits - profits_d
    tax_f = []
    for i in range(1995, 2014):
        tax_f.append(calcWAvgTaxRate(i))
    ftc_gross = profits_f * tax_f / 100.
    adjfactor = sum(ftc_actual / ftc_gross) / 19.
    return adjfactor


def calcIDAdjustment(corp, eta=0.4):
    """
    Calculates the adjustment factors for the corporate and noncorporate
    debt and interest.
    eta: retirement rate of existing debt
    """
    policy = Policy()
    policy_params_df = policy.parameters_dataframe()
    # Create Asset object
    asset = Asset(policy_params_df, corp)
    asset.calc_all()
    # Get asset forecast
    forecast = asset.get_forecast()
    # Create Debt object
    debt = Debt(policy_params_df, forecast, corp=corp)
    debt.calc_all()
    # Get unscaled net interest deduction
    NID_gross = debt.NID[38:54]
    # Get net interest deduction from historical IRS data
    if corp:
        NID_irs = np.array(data1.debt_data_corp['NID_IRS'])[38:54]
    else:
        NID_irs = np.array(data1.debt_data_noncorp['ID_Scorp'][38:54] +
                           data1.debt_data_noncorp['ID_sp'][38:54] +
                           data1.debt_data_noncorp['ID_partner'][38:54])
    NID_scale = sum(NID_irs / NID_gross) / 16.0  # 16 = 54 - 38
    return NID_scale


# Calculate the adjustment and dynamic parameters for AMT & PYMTC
all_amt_params = calcAMTparams2()
# Calculate the FTC adjustment parameters
adjfactor_ftc_corp = calcFTCAdjustment()



"""
Section 2. Calculation of pass-through shares
Note: All shares are estimated for 2013.
"""


# Total depreciation
totaldep = (data1.partner_data['dep_total'][19] +
            data1.Scorp_data['dep_total'][18] +
            data1.sp_data['dep_total'][16])
# Depreciation shares for S corporations (by income status)
depshare_scorp_posinc = data1.Scorp_data['dep_posinc'][18] / totaldep
depshare_scorp_neginc = (data1.Scorp_data['dep_total'][18] / totaldep
                         - depshare_scorp_posinc)
# Depreciation shares for sole proprietorships (by income status)
depshare_sp_posinc = data1.sp_data['dep_posinc'][16] / totaldep
depshare_sp_neginc = (data1.sp_data['dep_total'][16] / totaldep
                      - depshare_sp_posinc)
# Depreciation shares for partnerships (by income status)
depshare_partner_posinc = data1.partner_data['dep_posinc'][19] / totaldep
depshare_partner_neginc = (data1.partner_data['dep_total'][19] / totaldep
                           - depshare_partner_posinc)
# Total net interest deduction, excluding finance sector and holding companies
totalint_exfin = (data1.partner_data['intpaid_total'][19]
                  + data1.Scorp_data['intpaid_total'][18]
                  + data1.sp_data['mortintpaid'][16]
                  + data1.sp_data['otherintpaid'][16]
                  - data1.partner_data['intpaid_fin_total'][19]
                  - data1.Scorp_data['intpaid_fin'][18]
                  - data1.sp_data['mortintpaid_fin'][16]
                  - data1.sp_data['otherintpaid_fin'][16])
# Net interest share for S corporations (by income status)
intshare_scorp_posinc = ((data1.Scorp_data['intpaid_posinc'][18]
                          - data1.Scorp_data['intpaid_fin_posinc'][18])
                         / totalint_exfin)
intshare_scorp_neginc = ((data1.Scorp_data['intpaid_total'][18]
                          - data1.Scorp_data['intpaid_fin'][18])
                         / totalint_exfin - intshare_scorp_posinc)
# Net interest share for sole proprietorships (by income status)
intshare_sp_posinc = ((data1.sp_data['mortintpaid_posinc'][16]
                       + data1.sp_data['otherintpaid_posinc'][16]
                       - data1.sp_data['mortintpaid_fin_posinc'][16]
                       - data1.sp_data['otherintpaid_fin_posinc'][16])
                      / totalint_exfin)
intshare_sp_neginc = ((data1.sp_data['mortintpaid'][16]
                       + data1.sp_data['otherintpaid'][16]
                       - data1.sp_data['mortintpaid_fin'][16]
                       - data1.sp_data['otherintpaid_fin'][16]) /
                      totalint_exfin - intshare_sp_posinc)
intshare_partner_posinc = ((data1.partner_data['intpaid_posinc'][19]
                            - data1.partner_data['intpaid_fin_posinc'][19])
                           / totalint_exfin)
intshare_partner_neginc = ((data1.partner_data['intpaid_total'][19]
                            - data1.partner_data['intpaid_fin_total'][19])
                           / totalint_exfin - intshare_partner_posinc)

# Save the adjustment factors and pass-through shares
adj_factors = {'param_amt': all_amt_params[0],
               'amt_frac': all_amt_params[1],
               'userate_pymtc': all_amt_params[2],
               'trans_amt1': all_amt_params[3],
               'trans_amt0': all_amt_params[4],
               'ftc': adjfactor_ftc_corp}
passthru_factors = {'dep_scorp_pos': depshare_scorp_posinc,
                    'dep_scorp_neg': depshare_scorp_neginc,
                    'dep_sp_pos': depshare_sp_posinc,
                    'dep_sp_neg': depshare_sp_neginc,
                    'dep_part_pos': depshare_partner_posinc,
                    'dep_part_neg': depshare_partner_neginc,
                    'int_scorp_pos': intshare_scorp_posinc,
                    'int_scorp_neg': intshare_scorp_neginc,
                    'int_sp_pos': intshare_sp_posinc,
                    'int_sp_neg': intshare_sp_neginc,
                    'int_part_pos': intshare_partner_posinc,
                    'int_part_neg': intshare_partner_neginc}
df_adjf = pd.DataFrame({k: [adj_factors[k]] for k in adj_factors})
df_adjf.to_csv('biztax/adjfactors.csv', index=False)
df_pts = pd.DataFrame({k: [passthru_factors[k]] for k in passthru_factors})
df_pts.to_csv('biztax/passthru_shares.csv', index=False)
