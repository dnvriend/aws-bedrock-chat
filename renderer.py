import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import xml.etree.ElementTree as ET

def render_visualization(content):
    try:
        root = ET.fromstring(content)
        viz_type = root.get('type', '').lower()

        if viz_type == 'file':
            options = root.find('options')
            if options is not None:
                filename = options.find('filename').text
                if filename and os.path.exists(filename):
                    with open(filename, 'r') as file:
                        content = file.read()
                    return render_visualization(content)
                else:
                    st.warning(f"File not found: {filename}")
                    return

        # Rest of the rendering logic remains the same
        data_element = root.find('data')
        if data_element is None or len(data_element) == 0:
            st.warning("No data provided for visualization.")
            return

        data = []
        for item in data_element:
            data.append({child.tag: child.text for child in item})

        df = pd.DataFrame(data)

        if df.empty:
            st.warning("Data frame is empty. Cannot render visualization.")
            return

        options_element = root.find('options')
        options = {}
        if options_element is not None:
            options = {child.tag: child.text for child in options_element}
        title = options.get('title', '')

        fig = None

        # Basics
        if viz_type in ['scatter', 'line', 'area', 'bar', 'funnel', 'timeline']:
            fig = getattr(px, viz_type)(df, x=df.columns[0], y=df.columns[1], title=title)

        # Part-of-Whole
        elif viz_type in ['pie', 'sunburst', 'treemap', 'icicle', 'funnel_area']:
            fig = getattr(px, viz_type)(df, values=df.columns[1], names=df.columns[0], title=title)

        # 1D Distributions
        elif viz_type in ['histogram', 'box', 'violin', 'strip', 'ecdf']:
            fig = getattr(px, viz_type)(df, x=df.columns[0], title=title)

        # 2D Distributions
        elif viz_type in ['density_heatmap', 'density_contour']:
            fig = getattr(px, viz_type)(df, x=df.columns[0], y=df.columns[1], title=title)

        # Matrix or Image Input
        elif viz_type == 'imshow':
            fig = px.imshow(df, title=title)

        # 3-Dimensional
        elif viz_type in ['scatter_3d', 'line_3d']:
            fig = getattr(px, viz_type)(df, x=df.columns[0], y=df.columns[1], z=df.columns[2], title=title)

        # Multidimensional
        elif viz_type == 'scatter_matrix':
            fig = px.scatter_matrix(df, dimensions=df.columns, title=title)
        elif viz_type in ['parallel_coordinates', 'parallel_categories']:
            fig = getattr(px, viz_type)(df, title=title)

        # Tile Maps
        elif viz_type in ['scatter_mapbox', 'line_mapbox', 'choropleth_mapbox', 'density_mapbox']:
            fig = getattr(px, viz_type)(df, lat='latitude', lon='longitude', title=title)
            fig.update_layout(mapbox_style="open-street-map")

        # Outline Maps
        elif viz_type in ['scatter_geo', 'line_geo', 'choropleth']:
            fig = getattr(px, viz_type)(df, locations='iso_alpha', color=df.columns[1], title=title)

        # Polar Charts
        elif viz_type in ['scatter_polar', 'line_polar', 'bar_polar']:
            fig = getattr(px, viz_type)(df, r=df.columns[1], theta=df.columns[0], title=title)

        # Ternary Charts
        elif viz_type in ['scatter_ternary', 'line_ternary']:
            fig = getattr(px, viz_type)(df, a=df.columns[0], b=df.columns[1], c=df.columns[2], title=title)

        # Tables
        elif viz_type in ['table', 'interactive_table']:
            fig = go.Figure(data=[go.Table(
                header=dict(values=list(df.columns),
                            fill_color='paleturquoise',
                            align='left'),
                cells=dict(values=[df[col] for col in df.columns],
                           fill_color='lavender',
                           align='left'))
            ])
            fig.update_layout(title=title)

        if fig:
            fig.update_layout(
                title={
                    'text': title,
                    'y':0.9,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'
                }
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning(f"Unsupported visualization type: {viz_type}")
    except ET.ParseError:
        st.warning("Invalid XML format for visualization data.")
    except Exception as e:
        st.error(f"Error rendering visualization: {str(e)}")
        st.code(content, language="xml")

def process_content(content):
    parts = content.split('<visualization')

    # Process the initial non-XML content, if any
    if parts[0].strip():
        st.markdown(parts[0].strip())

    # Process each XML block
    for part in parts[1:]:
        xml_parts = part.split('</visualization>', 1)
        if len(xml_parts) == 2:
            xml_string = '<visualization' + xml_parts[0] + '</visualization>'
            render_visualization(xml_string)

            # Process any non-XML content after the visualization block
            if xml_parts[1].strip():
                st.markdown(xml_parts[1].strip())
        else:
            # Handle case where </visualization> tag is missing
            st.warning("Malformed visualization XML block detected.")
            st.code('<visualization' + part, language="xml")