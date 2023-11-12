import folium
import leafmap.foliumap as leafmap

# from dashboard_shared import Components, Table, export_df
# from districts.generaleneral import Data

class Map:
	def __init__(self,draw_control=False,google_map="HYBRID"):
		self.map = leafmap.Map(
			google_map=google_map,
			draw_control=draw_control,
		)

	def add_boundaries(self,boundaries):
		self.map.add_gdf(boundaries,layer_name="Boundaries",info_mode='on_click',)

	def add_markers_and_labels(self,gdf,label_col,color=None,color_col=None,icon='glyphicon glyphicon-tint',prefix='glyphicon',hover_cols='all',name=None,header_name=None):
		
		for i,row in gdf.iterrows():
			if color_col:
				color = row[color_col]
			# st.dataframe(row['COUNTY'])

			if name:
				row['Point Type'] = name

			frame=row.to_frame()

			popup = frame.to_html(
				header=False,
				escape=False,
				render_links=True,
				# col_space=10,
				border=3,
				)
			if hover_cols == 'all':
				tooltip = popup
			else:
				# add point type to hover_cols if not there
				if name:
					if 'Point Type' not in hover_cols:
						hover_cols.insert(0,'Point Type')
				
				
				# st.dataframe(row.to_frame())
				tooltip = frame.loc[hover_cols].to_html(
					header=False,
					escape=False,
					render_links=True,
					# col_space=10,
					border=3,
					)
			if header_name:
				popup = f"<h3>{header_name}</h3>" + popup
				tooltip = f"<h3>{header_name}</h3>" + tooltip

			
			# https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_html.html
			self.map.add_marker(
				(row.geometry.y,row.geometry.x),
				popup=popup,
				tooltip=tooltip,
				draggable=True,
				# tooltip=f"{row.iloc[:].to_dict() }",
				icon=folium.Icon(
					color=color,
					icon=icon,
					prefix=prefix,
					label=label_col,
				),
				)
		gdf['latitude'] = gdf.geometry.y
		gdf['longitude'] = gdf.geometry.x
		self.map.add_labels(
			data=gdf,
			x='longitude',
			y='latitude',
			column=label_col,
			font_color='white',
			font_size='12pt',
		)