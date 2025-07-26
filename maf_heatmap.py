import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ----------------------------
# PAGE SETUP
# ----------------------------
st.set_page_config(page_title="MAF Heatmap Viewer", layout="wide")
st.title("📊 MAF and Sample Count Heatmaps by MAP and RPM")

# ----------------------------
# FILE UPLOADS
# ----------------------------
uploaded_file = st.file_uploader("Step 1: Upload your Log File (CSV)", type=["csv"])
mapping_file = st.file_uploader("Step 2: Upload Column Mapping File (CSV)", type=["csv"])

if uploaded_file is not None and mapping_file is not None:
    # Load data
    df = pd.read_csv(uploaded_file)
    mapping_df = pd.read_csv(mapping_file)
    mapping_dict = dict(zip(mapping_df['original'], mapping_df['new']))
    df.rename(columns=mapping_dict, inplace=True)

    # Validate columns
    required_columns = ['MAP_mbar', 'RPM', 'MAF_gps']
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        st.error(f"Missing required columns after mapping: {', '.join(missing_cols)}")
        st.stop()

    # Clean data
    df = df.dropna(subset=required_columns)
    df = df[(df['MAP_mbar'] > 0) & (df['RPM'] > 0) & (df['MAF_gps'] > 0)]

    # Binning
    df['RPM_bin'] = (df['RPM'] // 500) * 500
    df['MAP_bin'] = (df['MAP_mbar'] // 50) * 50

    # Create pivot tables
    maf_map = df.pivot_table(index='MAP_bin', columns='RPM_bin', values='MAF_gps', aggfunc='mean')
    sample_count_map = df.pivot_table(index='MAP_bin', columns='RPM_bin', values='MAF_gps', aggfunc='count')

    # Sort so that higher MAP is on top
    maf_map = maf_map.sort_index(ascending=False)
    sample_count_map = sample_count_map.sort_index(ascending=False)

    # ----------------------------
    # PLOTTING FUNCTION
    # ----------------------------
    def plot_annotated_heatmap(z_data, x_data, y_data, title, colorscale, colorbar_title, value_format):
        text = [[f"{val:{value_format}}" if pd.notnull(val) else "" for val in row] for row in z_data.values]

        fig = go.Figure(data=go.Heatmap(
            z=z_data.values,
            x=x_data,
            y=y_data,
            colorscale=colorscale,
            colorbar=dict(title=colorbar_title),
            text=text,
            texttemplate="%{text}",
            hoverinfo='x+y+z'
        ))

        fig.update_layout(
            title=title,
            xaxis_title="RPM (bin)",
            yaxis_title="MAP (mbar, bin)"
        )
        return fig

    # ----------------------------
    # DISPLAY SIDE-BY-SIDE
    # ----------------------------
    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(
            plot_annotated_heatmap(
                maf_map,
                maf_map.columns,
                maf_map.index,
                "Average MAF (g/s) by MAP and RPM",
                "Viridis",
                "Avg MAF (g/s)",
                ".1f"
            ),
            use_container_width=True
        )

    with col2:
        st.plotly_chart(
            plot_annotated_heatmap(
                sample_count_map,
                sample_count_map.columns,
                sample_count_map.index,
                "Sample Count by MAP and RPM",
                "Blues",
                "Sample Count",
                ".0f"
            ),
            use_container_width=True
        )

else:
    st.info("📁 Please upload both the log file and the mapping file to continue.")
