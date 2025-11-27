FROM almalinux:9.5

# Set working directory
WORKDIR /usr/src/app

#Install crontab
#RUN yum -y install cronie python3-pip git
RUN mkdir -p /data/cache
RUN yum -y install python3-pip git
#COPY crontab /etc/cron.d/crontab
#RUN chmod 0644 /etc/cron.d/crontab &&\
#    crontab /etc/cron.d/crontab

COPY requirements.txt ./

#Install python dependencies
RUN python3 -m pip config set global.break-system-packages true && pip install --no-cache-dir -r requirements.txt

#Copy app specific files and set permissions
COPY scitags_registry_map.py .
RUN chmod 755 scitags_registry_map.py

ENTRYPOINT ["/usr/src/app/scitags_registry_map.py", "--verbose", "--output-yaml", "/data/cache", "--periodic", "604800"]
