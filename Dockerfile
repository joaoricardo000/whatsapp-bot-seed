FROM ubuntu:14.04

MAINTAINER Joao Ricardo "joaoricardo000@gmail.com"

RUN apt-get update && apt-get upgrade -y

# Dependencies
RUN apt-get install -y python2.7 python-dev python-pip python-virtualenv &&\
	apt-get install -y libfontconfig libjpeg-dev zlib1g-dev &&\
	apt-get install -y git curl supervisor espeak

# Node installation to use pageres
RUN curl -sL https://deb.nodesource.com/setup_4.x | sudo -E bash - &&\
	apt-get install -y nodejs

RUN npm -g install pageres-cli

# Copying files
COPY src/ /whatsapp-bot
COPY opt/requirements.pip /requirements.pip
COPY opt/supervisor.conf /etc/supervisor/conf.d
COPY opt/patch.sh /patch.sh

# Create virtualenv with requirements
RUN virtualenv venv && /./venv/bin/pip install -r requirements.pip


# Apply patches
RUN chmod +x /patch.sh
RUN /./patch.sh

EXPOSE 9005

############## EDIT
# Whatsapp Credentials:
ENV WHATSAPP_LOGIN="5544999999999"
ENV WHATSAPP_PW="xxxxxxxxxxxxxxxxxxxxxxxx="
# Bing API KEY for image search
ENV BING_API_KEY=""
# Add a cellphone number to set as admin
ENV WHATSAPP_ADMIN=""
############## /EDIT

CMD ["/usr/bin/supervisord"]