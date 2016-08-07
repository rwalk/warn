#!/bin/env bash

# get docker
curl -sSL https://get.docker.com/ | sh

# add ubuntu user
sudo usermod -aG docker ubuntu

# preqs
sudo apt-get install -y git python3-pip python-virtualenv

# clone repo
git config --global credential.helper 'cache --timeout=3600'
git clone https://github.com/rwalk/warn

# docker compose
sudo pip3 install docker-compose

# map 80 to 8080
iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8080

# filebeat
curl -L -O https://download.elastic.co/beats/filebeat/filebeat_1.2.3_amd64.deb
sudo dpkg -i filebeat_1.2.3_amd64.deb

# log directory
mkdir /var/log/warn
chown -R ubuntu:ubuntu /var/log/warn
chmod 0777 /var/log/warn

# reboot
sudo apt-get -y update
sudo apt-get -y upgrade
sudo reboot now


