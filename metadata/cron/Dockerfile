FROM ubuntu:latest

WORKDIR /usr/src/app

COPY run_cron.sh ./
RUN chmod 755 run_cron.sh
COPY install_crontab.sh ./
RUN chmod 755 install_crontab.sh
RUN apt-get update && \
    apt-get install -y cron python3 python3-pip git && \
    apt-get clean autoclean && \
    apt-get autoremove --yes && \
    rm -rf /var/lib/{apt,dpkg,cache,log}/

CMD [ "./run_cron.sh" ]
