#!/bin/env bash

# get docker
curl -sSL https://get.docker.com/ | sh

# add ubuntu user
sudo usermod -aG docker ubuntu

# preqs
sudo apt-get install -y git python3-pip python-virtualenv

# clone repo
git clone https://github.com/rwalk/warn

# docker compose
sudo pip3 install docker-compose

# map 80 to 8080
iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8080

# reboot
sudo apt-get -y update
sudo apt-get -y upgrade
sudo reboot now


