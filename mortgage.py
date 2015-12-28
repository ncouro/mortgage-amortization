import numpy as np
import logging


def calc_monthly_repayments(principal, interest_rate_monthly, nb_payments):
    monthly_repayment = principal * interest_rate_monthly * (1 + interest_rate_monthly) ** nb_payments / ( (1 + interest_rate_monthly) ** nb_payments - 1)
    return monthly_repayment


def calc_amortization_schedule(principal, mortgage_term_years, interest_rate_table, monthly_overpayment=0):
    remaining_principal = principal;
    principal_repaid = 0
    total_paid = 0
    total_interest_paid = 0

    nb_payments = mortgage_term_years * 12;
    overpayment_limit_principal = .10;

    output = {'year':                        np.full(nb_payments, np.NAN),
              'monthly_payment':             np.full(nb_payments, np.NAN),
              'monthly_principal_repayment': np.full(nb_payments, np.NAN),
              'monthly_interest_payment':    np.full(nb_payments, np.NAN),
              'principal_repaid':            np.full(nb_payments, np.NAN),
              'total_paid':                  np.full(nb_payments, np.NAN),
              }

    monthly_repayment = calc_monthly_repayments(remaining_principal, interest_rate_table[0], nb_payments)

    # Monthly repayments (UK style)
    for month_idx in range(0, nb_payments):
        year_idx = int(month_idx / 12)

        # Has the interest rate changed?
        if year_idx in interest_rate_table.keys() and month_idx % 12 == 0:
            interest_rate = interest_rate_table[year_idx] / 12.0
            monthly_repayment = calc_monthly_repayments(remaining_principal, interest_rate, nb_payments - month_idx)

        if remaining_principal > 0:
            if monthly_overpayment > overpayment_limit_principal * remaining_principal:
                monthly_overpayment_limited = overpayment_limit_principal * remaining_principal
                logging.debug(
                    "Overpayment limited to {0:2f} at period {1}".format(monthly_overpayment_limited, month_idx))
            else:
                monthly_overpayment_limited = monthly_overpayment

            interest_payment = interest_rate * remaining_principal
            principal_payment = monthly_repayment - interest_payment + monthly_overpayment_limited
            monthly_payment = monthly_repayment + monthly_overpayment_limited
        else:
            interest_payment = 0.0
            principal_payment = 0.0
            monthly_payment = 0.0
            monthly_overpayment_limited = 0.0
            logging.debug('Repaid after {0} periods ( {1:.1f} years)'.format(month_idx, month_idx / 12.0))

        total_paid += monthly_payment
        principal_repaid += principal_payment
        remaining_principal -= principal_payment
        total_interest_paid += interest_payment

        output['year'][month_idx] = month_idx / 12.0
        output['monthly_payment'][month_idx] = monthly_payment
        output['monthly_principal_repayment'][month_idx] = monthly_repayment
        output['monthly_interest_payment'][month_idx] = interest_payment
        output['principal_repaid'][month_idx] = principal_repaid
        output['total_paid'][month_idx] = total_paid

    return output
