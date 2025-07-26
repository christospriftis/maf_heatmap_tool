import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.title("MAF and Sample Count Heatmaps by MAP and RPM")

# Step 1: Upload main CSV log file
uploaded_file = st.file_uploader("Step 1: Upload your Log File (CSV)", type=["csv"])

# Step 2: Upload mapping file
mapping_file = st.file_uploader("Step 2: Upload Column Mapping File (CSV)", type=["csv"])

if uploaded_file is not None and mapping_file is not None:
    # Load the main data and mapping
    df = pd.read_csv(uploaded_file)
    mapping_df = pd.read_csv(mapping_file)

    # Create dictionary from mapping file: {original: new}
    mapping_dict = dict(zip(mapping_df['original'], mapping_df['new']))

    # Rename columns in the data using the mapping
    df.rename(columns=mapping_dict, inplace=True)

    # Check for required standardized columns
    required_columns = ['MAP_mbar', 'RPM', 'MAF_gps']
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        st.error(f"Missing required columns after mapping: {', '.join(missing_cols)}")
        st.stop()

    # Drop missing or invalid values
    df = df.dropna(subset=['MAP_mbar', 'RPM', 'MAF_gps'])
    df = df[(df['MAP_mbar'] > 0) & (df['RPM'] > 0) & (df['MAF_gps'] > 0)]

    # Binning
    df['RPM_bin'] = (df['RPM'] // 500) * 500
    df['MAP_bin'] = (df['MAP_mbar'] // 50) * 50

    # Pivot tables
    maf_map = df.pivot_table(index='MAP_bin', columns='RPM_bin', values='MAF_gps', aggfunc='mean')
    sample_count_map = df.pivot_table(index='MAP_bin', columns='RPM_bin', values='MAF_gps', aggfunc='count')
    sample_count_map_int = sample_count_map.fillna(0).astype(int)

    # Plotting
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
    st.info("Please upload both the log file and the mapping file to continue.")
