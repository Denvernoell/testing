# app/Dockerfile

FROM python:3.9-slim

# WORKDIR \\ppeng.com\pzdata\docs\Project Resources\Ag Water\apps\district_management\Dockerfile
# WORKDIR I:\Project Resources\Ag Water\apps\district_management
# WORKDIR G:\Cucamonga Valley WD - 4026\402622002-Cucmonga Basin Safe Yield Study\400 GIS\Scripts\testing

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# RUN git clone https://github.com/streamlit/streamlit-example.git .
# WORKDIR app
COPY . .


RUN pip3 install -r requirements.txt

EXPOSE 8503

HEALTHCHECK CMD curl --fail http://localhost:8503/_stcore/health

ENTRYPOINT ["streamlit", "run", "cucamonga_app.py", "--server.port=8503", "--server.address=0.0.0.0"]