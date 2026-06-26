import numpy as np
import pandas as pd
from scipy.optimize import least_squares


print("✅ nk_model NEW VERSION LOADED")


def fit_nk(df):

    lambda_nm = df['lambda_nm'].to_numpy().astype(float)
    T_meas = df['T'].to_numpy().astype(float)
    R_meas = df['R'].to_numpy().astype(float)

    # 百分比轉換
    if T_meas.max() > 1.5:
        T_meas /= 100.0
    if R_meas.max() > 1.5:
        R_meas /= 100.0

    lambda_um = lambda_nm * 1e-3
    d_um = 1000.0
    n0 = 1.0

    # ==========================
    # nk model
    # ==========================
    def nk_model(lambda_um, p):
        A, B, C, K0, K1 = p
        n = A + B / lambda_um**2 + C / lambda_um**4
        k = np.clip(K0 + K1 / lambda_um**2, 0, None)
        return n, k

    # ==========================
    # slab TR
    # ==========================
    def slab_TR(lambda_um, p):
        n, k = nk_model(lambda_um, p)
        n_complex = n - 1j * k

        r = (n_complex - n0) / (n_complex + n0)
        R = np.abs(r)**2
        T = (4 * np.real(n_complex) * n0) / np.abs(n_complex + n0)**2

        alpha = 4 * np.pi * k / lambda_um
        A = np.exp(-alpha * d_um)

        denom = 1 - R**2 * A**2

        T_final = (T**2 * A) / denom
        R_final = R + (T**2 * R * A**2) / denom

        return R_final, T_final

    # ==========================
    # fitting
    # ==========================
    def residuals(p):
        R_calc, T_calc = slab_TR(lambda_um, p)
        return np.concatenate([(T_meas - T_calc), (R_meas - R_calc)])

    p0 = [1.52, 0.004, 0.0, 0.0, 0.0]
    result = least_squares(residuals, p0)

    p_opt = result.x

    # ==========================
    # ✅ 這段是你缺的（最重要）
    # ==========================
    n_fit, k_fit = nk_model(lambda_um, p_opt)
    R_fit, T_fit = slab_TR(lambda_um, p_opt)

    df['n_fit'] = n_fit
    df['k_fit'] = k_fit
    df['T_fit'] = T_fit*100
    df['R_fit'] = R_fit*100

    return df