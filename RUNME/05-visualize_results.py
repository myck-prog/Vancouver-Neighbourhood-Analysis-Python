# 05-visualize_results.py
# Jonghyeok Kim and Myckland Matthew

# Learned more of the visualization from Folium Plugins:
# 	https://python-visualization.github.io/folium/plugins.html
# Learned more about Cloropleth Map from:
# 	http://python-visualization.github.io/folium/quickstart.html#Choropleth-maps

import folium
from folium.plugins import MarkerCluster
import geopandas as gpd
import json
import numpy as np
import pandas as pd
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import webbrowser


def get_nbh(skytrain, nbhs):
	for row in nbhs.itertuples():
		if row.Poly.contains(skytrain):
			return row.Index

	return None


def get_coords(geom):
		return geom['coordinates'][0]


def main():
	pd.set_option('mode.chained_assignment', None)

	# Read in data to map
	local_boundary = pd.read_csv('datafiles/input_files/local-area-boundary.csv',sep=';',index_col='Name')
	resto_data     = pd.read_csv('datafiles/yelp_scores.csv', index_col='neighbourhood')
	crime_data     = pd.read_csv('datafiles/safety_scores.csv', index_col='neighbourhood')
	skytrain_data  = pd.read_csv('datafiles/skytrain_scores.csv', index_col='neighbourhood')
	amenities      = pd.read_csv('datafiles/amenities_labelled_by_nbh.csv', index_col='neighbourhood')
	price_n_sqft   = pd.read_csv('datafiles/input_files/prices_per_sqft.csv', index_col='neighbourhood')
	price_n        = pd.read_csv('datafiles/price_scores.csv', index_col='neighbourhood')

	local_boundary['Geom'] = local_boundary['Geom'].apply(json.loads).apply(get_coords).apply(Polygon)

	# Join all the data together
	local_boundary = local_boundary.join(resto_data).join(crime_data).join(price_n)
	# print(local_boundary)

	# Extract geom data and transform GeoSeries to Json
	geo_jason = gpd.GeoSeries(local_boundary['Geom']).simplify(tolerance=0.001).to_json()
	local_boundary['id'] = local_boundary.index
	score = local_boundary[['id','yelp','safety','price']]
	score['id'] = score['id'].astype(str)

	m = folium.Map(location=[49.251, -123.1280], zoom_start=13)

	# Plot restaurant scores
	folium.Choropleth(
		geo_data=geo_jason,
		name="Yelp Restaurant Score",
		data=score,
		columns=["id", "yelp"],
		key_on="feature.id",
		fill_color="BuPu",
		fill_opacity=0.5,
		line_opacity=0.8,
		legend_name="Yelp Restaurant Score",
		bins=8,
		reset = True,
			show=False
			).add_to(m)

	# Plot crime scores
	folium.Choropleth(
		geo_data=geo_jason,
		name="Safety Score",
		data=score,
		columns=["id", "safety"],
		key_on="feature.id",
		fill_color="YlGn",
		fill_opacity=0.6,
		line_opacity=0.8,
		legend_name="Safety Score",
		bins=8,
		show=False
		).add_to(m)

	# Plot home sale price scores
	folium.Choropleth(
		geo_data=geo_jason,
		name="Home Sale Price Score",
		data=score,
		columns=["id", "price"],
		key_on="feature.id",
		fill_color="YlOrRd",
		fill_opacity=0.7,
		line_opacity=0.2,
		legend_name="Home Sale Price Score",
		bins=5,
		show=False
	).add_to(m)


	# Create amenities markers
	# Divide into food and non-food amenities
	amen_non_food_categories = ['education/childcare', 'money', 'arts/culture', 'healthcare', 'cars']
	amen_non_food_names = ['Educational or Childcare Facilities', 'Financial Institutions', 'Artistic or Cultural Landmarks', 'Healthcare Clinics', 'Automobile Services']
	amen_food = 'food/drink'

	# Create color list
	nf_color_list = ["blue", "Red", "Yellow", "Green", "Orange"]
	f_color_list =['purple']

	# Plot non-food amenities on map
	for i, amen in enumerate(amen_non_food_categories):
		amenity = amenities[amenities['category'] == amen]
		locations = amenity[['lat', 'lon']]
		locationlist = locations.values.tolist()
		amen = folium.FeatureGroup(name=amen_non_food_names[i],show=False).add_to(m)
		for point in locationlist:
			amen.add_child(folium.CircleMarker(point, radius=2, color=nf_color_list[i], opacity=0.6))

	# Plot food amenities using cluster marker
	amenity = amenities[amenities['category'] == amen_food]
	locations = amenity[['lat', 'lon']]
	locationlist = locations.values.tolist()
	food_cluster = MarkerCluster(name = 'Places to Buy Food or Drinks',show=False).add_to(m)
	for point in locationlist:
		folium.CircleMarker(point, radius=2, color=f_color_list[0], opacity=0.6).add_to(food_cluster)

	# Plot Vancouver Skytrain station locations
	skytrain = pd.read_csv('datafiles/input_files/skytrain_locations.csv')

	local_boundary.reset_index(inplace=True)
	train_boundaries = pd.DataFrame(local_boundary['Name']).sort_values('Name')
	train_boundaries['Poly'] = local_boundary['Geom']
	train_boundaries.set_index('Name', inplace=True)

	# Turn the skytrain locations into geometric points and identify which neighbourhood they belong to.
	coordinate = pd.Series(zip(skytrain.iloc[:,2], skytrain.iloc[:,1]))
	points = coordinate.apply(Point)
	skytrain['neighbourhood'] = points.apply(get_nbh, nbhs=train_boundaries)

	# Drop stations outside of Vancouver
	skytrain = skytrain[skytrain['neighbourhood'].notna()].copy()
	skytrain = skytrain.reset_index(drop=True)
	# print(skytrain)

	sky_locs = skytrain[['lat','lon']].values.tolist()
	skytrain_size = len(skytrain)

	# Add Skytrain marker
	skytrain_marker = folium.FeatureGroup('Skytrain Stations',show=False).add_to(m)
	for i, station in enumerate(sky_locs):
		skytrain_marker.add_child(folium.Marker(station,popup=skytrain['station'][i],tooltip = 'Click for Station Name',icon=folium.Icon(color='darkred',icon='train',prefix='fa')))


	# Plot neighbourhood names
	name_list = folium.FeatureGroup('Neighbourhood Name').add_to(m)
	for _, r in local_boundary.iterrows():
		sim_geo = gpd.GeoSeries(r['Geom']).simplify(tolerance=0.001)
		geo_j = sim_geo.to_json()
		name_list.add_child(folium.GeoJson(data=geo_j,style_function=lambda x: {'fillOpacity': 0, 'color': 'Black', 'weight': 1},tooltip=r['Name']))

	folium.LayerControl(autoZIndex=True).add_to(m)


	# Permission to adapt the template from Colin:
	# 	https://gist.github.com/ColinTalbert/18f8901fc98f109f2b71156cf3ac81cd
	# Open Issues solution from "How can I add a legend to a folium map":
	# 	https://github.com/python-visualization/folium/issues/528

	from branca.element import Template, MacroElement

	template = """
	{% macro html(this, kwargs) %}

	<!doctype html>
	<html lang="en">
	<head>
	<meta charset="utf-8">
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<title>Mapping of Vancouver</title>
	<link rel="stylesheet" href="//code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css">

	<script src="https://code.jquery.com/jquery-1.12.4.js"></script>
	<script src="https://code.jquery.com/ui/1.12.1/jquery-ui.js"></script>
	
	<script>
	$( function() {
		$( "#maplegend" ).draggable({
						start: function (event, ui) {
							$(this).css({
								right: "auto",
								top: "auto",
								bottom: "auto"
							});
						}
					});
	});

	</script>
	</head>
	<body>


	<div id='maplegend' class='maplegend' 
		style='position: absolute; z-index:9999; border:2px solid grey; background-color:rgba(255, 255, 255, 0.8);
		border-radius:6px; padding: 10px; font-size:14px; right: 20px; bottom: 20px;'>

	<div class='legend-title'>Dragable Legend  <br>Choose Amenities with the Checkbox Layer</div>
	<div class='legend-scale'>
	<ul class='legend-labels'>
		<li><span style='background:blue;opacity:0.7;'></span>Educational or Childcare Facilities</li>
		<li><span style='background:Red;opacity:0.7;'></span>Financial Institutions</li>
		<li><span style='background:Yellow;opacity:0.7;'></span>Artistic or Cultural Landmarks</li>
		<li><span style='background:Green;opacity:0.7;'></span>Helathcare Clinics</li>
		<li><span style='background:Purple;opacity:0.7;'></span>Places to Buy Food or Drinks</li>
		<li><span style='background:Orange;opacity:0.7;'></span>Automobile Services</li>

	</ul>
	</div>
	</div>
	
	</body>
	</html>

	<style type='text/css'>
	.maplegend .legend-title {
		text-align: left;
		margin-bottom: 5px;
		font-weight: bold;
		font-size: 90%;
		}
	.maplegend .legend-scale ul {
		margin: 0;
		margin-bottom: 5px;
		padding: 0;
		float: left;
		list-style: none;
		}
	.maplegend .legend-scale ul li {
		font-size: 80%;
		list-style: none;
		margin-left: 0;
		line-height: 18px;
		margin-bottom: 2px;
		}
	.maplegend ul.legend-labels li span {
		display: block;
		float: left;
		height: 16px;
		width: 30px;
		margin-right: 5px;
		margin-left: 0;
		border: 1px solid #999;
		}
	.maplegend .legend-source {
		font-size: 80%;
		color: #777;
		clear: both;
		}
	.maplegend a {
		color: #777;
		}
	</style>
	{% endmacro %}"""

	macro = MacroElement()
	macro._template = Template(template)

	m.get_root().add_child(macro)

	m.save('figures/Vancouver_Neighbourhood_Maps.html')
	webbrowser.open('figures/Vancouver_Neighbourhood_Maps.html',new=2)


if __name__ == '__main__':
	main()
