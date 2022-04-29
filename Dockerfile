# start by pulling the python image
FROM python:3.9.12-buster

# copy the requirements file into the image
COPY ./requirements.txt /opt/requirements.txt

# switch working directory
WORKDIR /opt

# install the dependencies and packages in the requirements file
RUN pip install --upgrade wheel
RUN pip install -r requirements.txt

# copy every content from the local file to the image
COPY . /opt

CMD python prepare.py && gunicorn --bind 0.0.0.0:$PORT app:app