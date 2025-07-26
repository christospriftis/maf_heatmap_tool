import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.title("MAF and Sample Count Heatmaps by MAP and RPM")

# File uploader
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file is not None:
    # Load data
    df = pd.read_csv(uploaded_file)
    
    # Rename columns (adjust if your CSV has different headers)
    df.rename(columns={
        'General: Intake manifold pressure (G71)': 'MAP_mbar',
        'General: Intake air temperature (G42)': 'IAT_C',
        'General: Engine speed (G28)': 'RPM',
        'Emission reduction (secondary air injection: Mass air flow sensor (G70)': 'MAF_gps',
        'Lambda control (lambda sensor voltages): Lambda control bank 1 (specified)': 'AFR_specified',
        'General: Injection timing': 'Injector_PW_ms',
        'Lambda control: Lambda control bank 1 sensor 1': 'STFT_percent'
    }, inplace=True)

    # Drop missing or zero values
    df = df.dropna(subset=['MAP_mbar', 'IAT_C', 'RPM', 'MAF_gps', 'AFR_specified', 'Injector_PW_ms'])
    df = df[(df['MAP_mbar'] > 0) & (df['RPM'] > 0) & (df['MAF_gps'] > 0)]

    # Binning
    df['RPM_bin'] = (df['RPM'] // 500) * 500
    df['MAP_bin'] = (df['MAP_mbar'] // 50) * 50

    # Pivot tables
    maf_map = df.pivot_table(index='MAP_bin', columns='RPM_bin', values='MAF_gps', aggfunc='mean')
    sample_count_map = df.pivot_table(index='MAP_bin', columns='RPM_bin', values='MAF_gps', aggfunc='count')
    sample_count_map_int = sample_count_map.fillna(0).astype(int)

    # Plotting side-by-side heatmaps with matplotlib and seaborn
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7))

    sns.heatmap(maf_map, cmap='viridis', annot=True, fmt=".1f", ax=ax1, cbar_kws={'label': 'Avg MAF (g/s)'})
    ax1.set_title('Average MAF (g/s) by MAP and RPM')
    ax1.set_xlabel('RPM (bin)')
    ax1.set_ylabel('MAP (mbar, bin)')
    ax1.invert_yaxis()

    sns.heatmap(sample_count_map_int, cmap='viridis', annot=True, fmt="d", ax=ax2, cbar_kws={'label': 'Sample Count'})
    ax2.set_title('Sample Count by MAP and RPM')
    ax2.set_xlabel('RPM (bin)')
    ax2.set_ylabel('MAP (mbar, bin)')
    ax2.invert_yaxis()

    plt.tight_layout()
    st.pyplot(fig)

else:
    st.info("Please upload a CSV file to see the heatmaps.")
