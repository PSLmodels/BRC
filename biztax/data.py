"""
Business-Taxation Data class.
"""
import os
import numpy as np
import pandas as pd
from taxcalc import read_egg_csv
from biztax.years import START_YEAR, END_YEAR, NUM_YEARS


class Data():
    """
    Constructor for the Data object.
    The purpose of this object is to read and contain all of the necessary
    datasets to run the analyses in Business-Taxation. This also provides a
    central mechanism for updating and improving the underlying data. One of
    the important features of the Data object is that it should not be changed
    by any other objects in Business-Taxation.
    """

    CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))
    CTAX_DATA_DIR = 'brc_data'

    def __init__(self):
        self.gfactors = Data.read_csv('gfactors.csv')
        self.historical_taxdata = Data.read_csv('historical_taxdata.csv')
        self.historical_combined = Data.read_csv(
            os.path.join(Data.CTAX_DATA_DIR, 'historical_combined.csv'))
        # Tax revenue data
        self.taxrev_data = Data.read_csv(
            os.path.join(Data.CTAX_DATA_DIR, 'taxrev.csv'))
        # Corporate tax data for 2013
        self.corp_tax2013 = Data.read_csv(
            os.path.join(Data.CTAX_DATA_DIR, 'corp_taxreturn_2013.csv'))
        # Data for FTC model
        self.ftc_taxrates_data = Data.read_csv(
            os.path.join(Data.CTAX_DATA_DIR, 'ftc_taxrates_data.csv'))
        self.ftc_gdp_data = Data.read_csv(
            os.path.join(Data.CTAX_DATA_DIR, 'ftc_gdp_data.csv'))
        self.ftc_other_data = Data.read_csv(
            os.path.join(Data.CTAX_DATA_DIR, 'ftc_other_data.csv'))
        self.cfc_data = Data.read_csv(
            os.path.join(Data.CTAX_DATA_DIR, 'cfc_data.csv'))
        self.dmne_data = Data.read_csv(
            os.path.join(Data.CTAX_DATA_DIR, 'dmne_data.csv'))
        self.reprate_forecast = Data.read_csv(
            os.path.join(Data.CTAX_DATA_DIR, 'repatriation_adjustment.csv'))
        # Data for Sec. 199
        self.sec199_data = Data.read_csv(
            os.path.join(Data.CTAX_DATA_DIR, 'sec199.csv'))
        # Investment and capital data
        self.investment_corp = Data.read_csv(
            os.path.join(Data.CTAX_DATA_DIR, 'investment_corp.csv'))
        self.investment_noncorp = Data.read_csv(
            os.path.join(Data.CTAX_DATA_DIR, 'investment_ncorp.csv'))
        self.capital_corp = Data.read_csv(
            os.path.join(Data.CTAX_DATA_DIR, 'capital_corp.csv'))
        self.capital_noncorp = Data.read_csv(
            os.path.join(Data.CTAX_DATA_DIR, 'capital_ncorp.csv'))
        self.investmentGfactors_data = Data.read_csv(
            os.path.join(Data.CTAX_DATA_DIR, 'investment_gfactors.csv'))
        # Tax depreciation information
        self.depreciationIRS_data = Data.read_csv(
            os.path.join(Data.CTAX_DATA_DIR, 'dep_data.csv'))
        self.bonus_data = Data.read_csv(
            os.path.join(Data.CTAX_DATA_DIR, 'bonus_data.csv'))
        # Debt data
        self.debt_data = Data.read_csv(
            os.path.join(Data.CTAX_DATA_DIR, 'debt_history.csv'))
        self.debt_forecast = Data.read_csv('debt_forecast.csv')
        self.debt_data_corp = Data.read_csv(
            os.path.join(Data.CTAX_DATA_DIR, 'corp_debt_data.csv'))
        self.debt_data_noncorp = Data.read_csv(
            os.path.join(Data.CTAX_DATA_DIR, 'noncorp_debt_data.csv'))
        # Pass-through IRS data
        self.partner_data = Data.read_csv(
            os.path.join(Data.CTAX_DATA_DIR, 'partnership_data.csv'))
        self.Scorp_data = Data.read_csv(
            os.path.join(Data.CTAX_DATA_DIR, 'scorp_data.csv'))
        self.sp_data = Data.read_csv(
            os.path.join(Data.CTAX_DATA_DIR, 'sp_nonfarm_data.csv'))
        # Defaults for posssible use (may be deprecated)
        self.econ_defaults = Data.read_csv(
            os.path.join(Data.CURRENT_PATH, 'mini_params_econ.csv'))
        self.rescale_corp = np.ones(NUM_YEARS)
        self.rescale_noncorp = np.ones(NUM_YEARS)
        # Read in adjustment factors
        adj_factors = Data.read_csv('adjfactors.csv')
        self.param_amt = adj_factors['param_amt'].values[0]
        self.amt_frac = adj_factors['amt_frac'].values[0]
        self.userate_pymtc = adj_factors['userate_pymtc'].values[0]
        self.trans_amt0 = adj_factors['trans_amt0'].values[0]
        self.trans_amt1 = adj_factors['trans_amt1'].values[0]
        self.adjfactor_ftc_corp = adj_factors['ftc'].values[0]
        # Read in pass-through shares
        passthru_factors = Data.read_csv('passthru_shares.csv')
        self.depshare_scorp_posinc = passthru_factors['dep_scorp_pos'].values[0]
        self.depshare_scorp_neginc = passthru_factors['dep_scorp_neg'].values[0]
        self.depshare_sp_posinc = passthru_factors['dep_sp_pos'].values[0]
        self.depshare_sp_neginc = passthru_factors['dep_sp_neg'].values[0]
        self.depshare_partner_posinc = passthru_factors['dep_part_pos'].values[0]
        self.depshare_partner_neginc = passthru_factors['dep_part_neg'].values[0]
        self.intshare_scorp_posinc = passthru_factors['int_scorp_pos'].values[0]
        self.intshare_scorp_neginc = passthru_factors['int_scorp_neg'].values[0]
        self.intshare_sp_posinc = passthru_factors['int_sp_pos'].values[0]
        self.intshare_sp_neginc = passthru_factors['int_sp_neg'].values[0]
        self.intshare_partner_posinc = passthru_factors['int_part_pos'].values[0]
        self.intshare_partner_neginc = passthru_factors['int_part_neg'].values[0]

    @staticmethod
    def read_csv(filename):
        """
        Returns Pandas DataFrame object containing data in specified filename,
        which is an absolute path to CSV file without the Data.CURRENT_PATH.
        """
        assert filename.endswith('.csv')
        fname = os.path.join(Data.CURRENT_PATH, filename)
        if os.path.exists(fname):
            dframe = pd.read_csv(fname)
        else:  # find file in conda package
            dframe = read_egg_csv(filename)  # pragma: no cover
        return dframe

    @staticmethod
    def econ_depr_df():
        """
        Retrieves the DataFrame with economic depreciation rates
        """
        df_econdepr1 = Data.read_csv(
            os.path.join(Data.CTAX_DATA_DIR,
                         'economic_depreciation_rates.csv'))
        # Extract each column as an array
        asset = np.asarray(df_econdepr1['Asset'])
        code = np.asarray(df_econdepr1['Code'])
        delta = np.asarray(df_econdepr1['Economic Depreciation Rate'])
        # Append values for residential categories
        asset = np.append(asset, ['Residential new',
                                  'Residential additions and alterations',
                                  'Residential major improvements',
                                  'Residential equipment'])
        code = np.append(code, ['RR10', 'RR20', 'RR30', 'RR40'])
        delta = np.append(delta, [delta[96], delta[96], delta[96], delta[36]])
        df_econdepr2 = pd.DataFrame({'Asset': asset, 'Code': code,
                                     'delta': delta})
        # Drop nonbusiness categories, land and inventories
        df_econdepr2.drop([28, 36, 56, 89, 90, 96, 97, 98],
                          axis=0, inplace=True)
        df_econdepr2.reset_index(drop=True, inplace=True)
        return df_econdepr2

    def taxdep_info_gross(self, extension):
        """
        Retrieves the basic DataFrame with tax depreciation information.
        """
        filename = 'tax_depreciation_' + extension + '.csv'
        taxdep1 = Data.read_csv(
            os.path.join(Data.CURRENT_PATH, filename))
        taxdep1.rename(columns={'GDS life': 'L_gds', 'ADS life': 'L_ads',
                                'Asset Type': 'Asset', 'GDS method': 'Method',
                                'Asset code': 'Code'},
                       inplace=True)
        return taxdep1.merge(right=self.econ_depr_df(), how='outer', on='Code')

    def update_rescaling(self, corparray, ncorparray):
        """
        Updates the rescaling factors associated with the Data class object
        """
        assert len(corparray) == NUM_YEARS
        assert len(ncorparray) == NUM_YEARS
        self.rescale_corp = corparray
        self.rescale_noncorp = ncorparray
