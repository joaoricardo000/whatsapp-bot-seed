#!/usr/bin/env bash
sudo apt-get install -y libjpeg-dev zlib1g-dev libfontconfig
sudo ln -s /usr/lib/x86_64-linux-gnu/libjpeg.so /usr/lib
sudo ln -s /usr/lib/x86_64-linux-gnu/libfreetype.so /usr/lib
sudo ln -s /usr/lib/x86_64-linux-gnu/libz.so /usr/lib
sudo npm -g install pageres-cli
sudo apt-get install -y espeak
