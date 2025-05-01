FROM metadata/cron:latest

# Set working directory
WORKDIR /usr/src/app

#Install crontab
COPY crontab /etc/cron.d/crontab
RUN chmod 0644 /etc/cron.d/crontab &&\
    crontab /etc/cron.d/crontab

COPY requirements.txt ./

#Install python dependencies
RUN python3 -m pip config set global.break-system-packages true && pip install --no-cache-dir -r requirements.txt

#Copy app specific files and set permissions
COPY cric_metadata_collector.py .
RUN chmod 755 cric_metadata_collector.py
