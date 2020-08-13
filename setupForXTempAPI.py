#!/bin/bash

sudo apt-get install python3 python3-pip 

TARGET=/usr/lib/python3.8

sudo pip3 install --target $TARGET flask
sudo pip3 install --target $TARGET waitress

