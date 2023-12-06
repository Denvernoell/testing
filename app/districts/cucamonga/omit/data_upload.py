import streamlit as st
import pandas as pd
import supabase

def main():
	bucket = st.session_state['client'].storage.get_bucket('cucamonga')
	# bucket = storage.get_bucket('cucamonga')
	# st.markdown(bucket)
	# st.markdown(supabase.__version__)
	# file = st.file_uploader("Upload a file", type="csv")
	file = st.file_uploader("Upload a file")
	if st.button("Upload file"):
		if file is not None:
			# bucket.upload_file(file, file.name)
			st.markdown(file)
			st.markdown(file.name)
			# file_path = 
			# path=open(file, 'rb'),
			from io import BytesIO
			import base64
			output = BytesIO()

		# wb = clean(file_path=file_path, length_axis_1=length, length_axis_3=width)
		# wb.save(output)
		# b64 = base64.b64encode(output.getvalue()).decode()
		# new_filename  = Path(file_path.name).stem + "_cleaned.xlsx"

		# # new_filename = f"{file_path.name.replace('.xlsx','')}_cleaned.xlsx"
		# st.markdown("#### Download File ###")
		# href = f'<a href="data:file/xlsx;base64,{b64}" download="{new_filename}">Download</a>'
		# st.markdown(href, unsafe_allow_html=True)


			bucket.upload(
				path=output,
				file=file.name
				)
