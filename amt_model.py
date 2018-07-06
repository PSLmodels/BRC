# set and calculate parameters
theta_set = [0.269045, 0.920237, 1]


def calcAMTparams():
    """
    Calculates the adjustment factors for the AMT and PYMTC
    """
    # Grab historical data
    amt_data2 = copy.deepcopy(amtdata2)
    Clist = amt_data2['C'].tolist()
    Alist = amt_data2['A'].tolist()[:20]
    Plist = amt_data2['P'].tolist()[:20]
    Slist = np.zeros(len(Alist))
    Slist[19] = 26.0
    AMT_rate = 0.2
    Ctax_rate = 0.347
    # Expand model backward based on defined value of S[19]
    for i in range(19):
        Slist[18-i] = Slist[19-i] + Plist[18-i] - Alist[18-i]
    gross_use_rate = sum([Plist[i] / Slist[i] for i in range(20)]) / 20.
    gamma = gross_use_rate / theta_set[0]
    nu = (sum([Alist[i] / Clist[i] for i in range(7, 20)]) / 13. *
          Ctax_rate / AMT_rate)
    return (gamma, nu)
#(adjfactor_pymtc_corp, adjfactor_amt_corp) = calcAMTparams()

amt_rates_default = np.asarray(btax_defaults['tau_amt'])
ctax_rates_default = np.asarray(btax_defaults['tau_c'])


def AMTmodel(amt_repeal_year=9e99, pymtc_repeal_year=9e99,
             amt_rates=amt_rates_default,
             ctax_rates=ctax_rates_default):
    """
    Calculates the AMT revenue and PYMTC for 2014-2027
    Parameters:
    amt_repeal_year: year corporate AMT repealed
    pymtc_repeal_year: year PYMTC repealed
    amt_rates: AMT rate for each year 2014-2027
    corporate income tax rate for each year 2014-2027
    """
    assert len(amt_rates) == 14
    assert len(ctax_rates) == 14
    amt_data2 = copy.deepcopy(amtdata2)
    Clist = amt_data2['C'].tolist()[19:]
    Alist = [amt_data2['A'][19]]
    Plist = [amt_data2['P'][19]]
    Slist = [26.0]
    Slist.append(Slist[0] + Alist[0] - Plist[0])
    for i in range(1, 15):
        # Determine AMT revenue
        if i + 2013 >= amt_repeal_year:
            Alist.append(0)
        else:
            Alist.append(Clist[i] * adjfactor_amt_corp *
                         min(amt_rates[i-1] / ctax_rates[i-1], 1))
        # Determine PYMTC
        if i + 2013 >= pymtc_repeal_year:
            Plist.append(0)
        elif i + 2013 < amt_repeal_year:
            Plist.append(Slist[i] * adjfactor_pymtc_corp * theta_set[0])
        elif i + 2013 == amt_repeal_year:
            Plist.append(Slist[i] * adjfactor_pymtc_corp * theta_set[1])
        else:
            Plist.append(Slist[i] * adjfactor_pymtc_corp * theta_set[2])
        Slist.append(Slist[i] + Alist[i] - Plist[i])
    # Rescale for any cross-sector shifting
    amt_final = np.asarray(Alist[1:]) * rescale_corp
    pymtc_final = np.asarray(Plist[1:]) * rescale_corp
    AMT_results = pd.DataFrame({'year': range(2014, 2028),
                                'amt': amt_final, 'pymtc': pymtc_final})
    return AMT_results
