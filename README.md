# Scitag firefly collector

# What is this?

This is software to collect firefly packets from the LHC experiment data transfer hosts.

The purpose of these firefly packets is to communicate metadata for LHC scientific flows (e.g., type of transfer, experiment information). The fireflies are generated by end hosts.

# How to run the pipeline

The pipeline writes collected fireflies to syslog files in the `./data` directory. It also uses filebeat and logstash and elasticsearch to push the data to Elasticsearch.

To configure the pipeline run `cp conf/logstash/99-outputs.conf.example conf/logstash/99-outputs.conf`. Open the copied file and enter the parameters for your Elasticsearch server. If you are using SSL, you will need to place your CA certificate at `./conf/certificates/elastic.cer`. You can name this something else, just modify `99-outputs.conf` accordingly.

With the Elastic parameters configured, bring up the pipeline as follows:

```
sudo docker-compose up -d
```

To verify firefly packets arriving, you can do:

```
% tail -f ./data/syslogs/messages
Sep 21 23:05:34 cc6d849e2f45 syslog-ng[1]: syslog-ng starting up; version='3.31.2'
Sep 21 23:08:20 umfs19 1 2021-09-21T23:08:20.575963+00:00 umfs19.aglt2.org flowd - firefly - {"flow-id": {"protocol": "tcp", "afi": "ipv4", "dst-ip": "131.225.105.11", "src-port": 43031, "src-ip": "192.41.231.128", "dst-port": 80}, "version": 1, "flow-lifecycle": {"state": "start", "start-time": "2021-09-21T23:08:20.576039+00:00", "current-time": "2021-09-21T23:08:20.576021+00:00"}, "context": {"experiment-id": 16, "application": "flowd v0.0.1", "activity-id": 1}}
```

You should see firefly records appear in Elasticsearch in the index `stardust_firefly-*`.
