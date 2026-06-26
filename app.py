import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from nk_model import fit_nk

st.set_page_config(page_title="Glass n/k Calculator", layout="wide")

st.title("🔬 Glass n / k Optical Fitting Tool")

uploaded_file = st.file_uploader("Upload Excel (lambda_nm, T, R)", type=["xlsx"])

if uploaded_file is not None:

    df = pd.read_excel(uploaded_file)

    st.subheader("📄 Raw Data")
    st.dataframe(df, use_container_width=True)

    # ==========================
    # ✅ Fitting
    # ==========================
    result_df = fit_nk(df)

    st.subheader("✅ Fitted Data")
    st.dataframe(result_df, use_container_width=True)
    
    # ✅ 👇 加在這裡（最重要）
    st.write("DEBUG columns:", result_df.columns)

    # ==========================
    # ✅ RMSE 計算
    # ==========================
    rmse_T = ((result_df['T'] - result_df['T_fit'])**2).mean()**0.5
    rmse_R = ((result_df['R'] - result_df['R_fit'])**2).mean()**0.5

    st.subheader("📊 Fit Error")
    st.write(f"RMSE (T) = {rmse_T:.6f}")
    st.write(f"RMSE (R) = {rmse_R:.6f}")

    
    # ==========================
    # ✅ 👉 放在這裡（Fit Quality）
    # ==========================
    st.subheader("✅ Fit Quality Evaluation")

    if rmse_T < 0.5 and rmse_R < 0.5:
        st.success("✅ Excellent Fit (RMSE < 0.5%)")

    elif rmse_T < 1 and rmse_R < 1:
        st.info("✅ Good Fit (RMSE < 1%)")

    elif rmse_T < 2 and rmse_R < 2:
        st.warning("⚠️ Acceptable Fit (RMSE < 2%)")

    else:
        st.error("❌ Poor Fit – Check model or data")



    # ==========================
    # ✅ n / k 同圖（雙軸）
    # ==========================
    fig_nk = go.Figure()

    fig_nk.add_trace(go.Scatter(
        x=result_df['lambda_nm'],
        y=result_df['n_fit'],
        name="n",
        yaxis="y1",
        mode="lines"
    ))

    fig_nk.add_trace(go.Scatter(
        x=result_df['lambda_nm'],
        y=result_df['k_fit'],
        name="k",
        yaxis="y2",
        mode="lines"
    ))

    fig_nk.update_layout(
        title="n & k vs Wavelength",
        xaxis=dict(title="Wavelength (nm)"),
        yaxis=dict(title="n"),
        yaxis2=dict(
            title="k",
            overlaying='y',
            side='right'
        ),
        template="plotly_white"
    )

    st.plotly_chart(fig_nk, use_container_width=True)

    # ==========================
    # ✅ T / R 擬合 vs 實測
    # ==========================
    fig_tr = go.Figure()

    # T measured
    fig_tr.add_trace(go.Scatter(
        x=result_df['lambda_nm'],
        y=result_df['T'],
        mode='markers',
        name='T (Measured)'
    ))

    # T fitted (%)
    fig_tr.add_trace(go.Scatter(
        x=result_df['lambda_nm'],
        y=result_df['T_fit'],
        mode='lines',
        name='T Fit (%)'

    ))

    # R measured
    fig_tr.add_trace(go.Scatter(
        x=result_df['lambda_nm'],
        y=result_df['R'],
        mode='markers',
        name='R (Measured)'
    ))

    # R fitted (%)
    fig_tr.add_trace(go.Scatter(
        x=result_df['lambda_nm'],
        y=result_df['R_fit'],
        mode='lines',
        name='R Fit (%)'
    ))

    fig_tr.update_layout(
        title="T / R: Measured vs Fitted",
        xaxis_title="Wavelength (nm)",
        yaxis_title="Value",
        template="plotly_white"
    )

    st.plotly_chart(fig_tr, use_container_width=True)

    # ==========================
    # ✅ Residual Plot
    # ==========================

    res_T = result_df['T'] - result_df['T_fit']
    res_R = result_df['R'] - result_df['R_fit']

    
    # ==========================
    # ✅ Residual Plot
    # ==========================
    fig_res = go.Figure()

    # T residual
    fig_res.add_trace(go.Scatter(
        x=result_df['lambda_nm'],
        y=res_T,
        mode='lines+markers',
        name='Residual T'
    ))

    # R residual
    fig_res.add_trace(go.Scatter(
        x=result_df['lambda_nm'],
        y=res_R,
        mode='lines+markers',
        name='Residual R'
    ))

    # ✅ 0 baseline（非常重要）
    fig_res.add_hline(y=0, line_dash="dash", line_color="black")

    fig_res.update_layout(
        title="Residual (Measured - Fitted)",
        xaxis_title="Wavelength (nm)",
        yaxis_title="Error (%)",
        template="plotly_white"
    )

    st.plotly_chart(fig_res, use_container_width=True)

    
    # ==========================
    # ✅ 👉 放在這裡（Residual 判斷）
    # ==========================
    import numpy as np

    mean_res_T = np.mean(res_T)
    mean_res_R = np.mean(res_R)

    if abs(mean_res_T) > 0.2:
        st.warning("⚠️ T residual shows systematic bias")

    if abs(mean_res_R) > 0.2:
        st.warning("⚠️ R residual shows systematic bias")



    # ==========================
    # ✅ 下載 Excel
    # ==========================
    output_file = "nk_result.xlsx"
    result_df.to_excel(output_file, index=False)

    with open(output_file, "rb") as f:
        st.download_button(
            label="📥 Download Result Excel",
            data=f,
            file_name="nk_result.xlsx"
        )
