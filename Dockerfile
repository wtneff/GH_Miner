FROM python:3.10

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/:backend/

WORKDIR /backend


# Need to replace certain values from original for docker environment
RUN sed -i 's/localhost/mysql/g' app/config.py # assumes the mysql container is named mysql
RUN sed -i 's/GITHUB_OAUTH_CLIENT_ID.*/GITHUB_OAUTH_CLIENT_ID = os.environ.get(\"GITHUB_OAUTH_CLIENT_ID\")/g' app/config.py
RUN sed -i 's/GITHUB_OAUTH_CLIENT_SECRET.*/GITHUB_OAUTH_CLIENT_SECRET = os.environ.get(\"GITHUB_OAUTH_CLIENT_SECRET\")/g' app/config.py
RUN sed -i 's/app.run.*/app.run(debug=True, host=\"0.0.0.0\")/g' run.py

CMD [ "python", "run.py" ]
