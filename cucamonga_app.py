import streamlit as st
import pandas as pd
# import supabase

from pathlib import Path
# data_path = Path(__file__).parent / "data"
asset_path = Path("assets")
from supabase import create_client, Client

from utils.dashboard_shared import Components, Table, District

C = Components("Cucamonga Basin")
C.header()
supabase: Client = create_client(st.secrets['supabase_url'],st.secrets['supabase_key'])
st.session_state['client'] = supabase
# st.markdown(supabase.storage().list_buckets())
# st.markdown(supabase.auth)


def login_page():
	# st.session_state['client'] = supabase.create_client(st.secrets['supabase_url'],st.secrets['supabase_key'])
	login_type = st.radio("New here?",["Login","Register"],horizontal=True)
	if login_type == "Login":
		with st.form(key='login'):
			email = st.text_input("Email")
			password = st.text_input("Password", type="password")
			# email = st.secrets['test_email']
			# password = st.secrets['test_password']
			submit_button = st.form_submit_button("Log in")

		if submit_button:
			try:
				st.session_state['user'] = st.session_state['client'].auth.sign_in_with_password(
					credentials={'email':email,'password':password}
					)
				st.session_state['Logged In'] = True
				add_sidebar()
			except Exception as e:
				st.error(e)
				st.error('Incorrect username or password')

	elif login_type == "Register":
		with st.form(key='register'):
			email = st.text_input("Email")
			password = st.text_input("Password", type="password")
			submit_button = st.form_submit_button("Register")
		if submit_button:
			try:
				st.session_state['user'] = st.session_state['client'].auth.sign_up(credentials={'email':email,'password':password})
				st.success('Check your email to confirm registration')
			except Exception as e:
				st.error('Check if you have already registered')
				st.error(e)


		# if (user == st.secrets['login_username'] and password == st.secrets['login_password']):

def add_sidebar():
	user_data = Table('user_permissions').df
	user_email = st.session_state['user'].dict()['user']['identities'][0]['identity_data']['email']
	st.session_state['user_email'] = user_email
	st.sidebar.markdown(f"Logged in as {user_email}")
	if st.sidebar.button('Logout'):
		st.session_state['Logged In'] = False
		st.session_state['user'] = None
		# st.rerun()


	try:
		# permissions = user_data.pipe(lambda df: df.loc[df['email'] == user_email]['districts'].iloc[0])
		permission_row = user_data.pipe(lambda df: df.loc[df['email'] == user_email].iloc[0])
		# st.dataframe(permission_row)
		pages = {}
		permission = permission_row['cucamonga']

		if permission in ['admin','CVWD','SAWC','WEWC']:
			pages['Cucamonga Basin'] = District(
				name='Cucamonga Basin',
				folder='cucamonga',
				pages = {
						"Well Dashboard":'well_dashboard',
						"Well Data Sheet":'well_data_sheet',
						# "Data Upload":'data_upload',
						"Input Table":'input_table',
						# "SDWIS Water Quality":'sdwis_wq_charts',
						# "Schema":'schema',
						'Settings':'settings',
					}
			)
		permissions = {
		'admin':'P&P',
		'CVWD':'Cucamonga Valley Water District',
		'SAWC':'San Antonio Water Company',
		'WEWC':'West End Consolidated Water Company',
		}

		st.session_state['agency'] = permissions[permission]
		# st.markdown(st.session_state['agency'])
		


		client_images = {
			"P&P":"PNP.png",
			"Cucamonga Valley Water District":"CVWD.png",
			"San Antonio Water Company":"SAWC.jpg",
			"West End Consolidated Water Company":'WEWC.png',
		}
		# client = st.selectbox("Select Client", client_images.keys())
		img_path = client_images[st.session_state['agency']]
		img = str(asset_path.joinpath(img_path))
		# st.markdown(img)
		st.sidebar.image(
			img,
			use_column_width=True)
		st.sidebar.markdown("---")
		
	except Exception as e:
		st.markdown("You don't have access to any districts")
		st.warning(e)
		permission_row = None
		pages = {}
	
	if pages != {}:
		district = pages[st.sidebar.radio('Categories', pages.keys())]
		st.sidebar.markdown("---")
		district.homepage()

if 'Logged In' not in st.session_state:
	st.session_state['Logged In'] = False

if st.session_state['Logged In']:
	add_sidebar()
	# st.rerun()
else:
	login_page()

C.footer()


