# whatsapp-bot-seed
A small python seed to create a Whatsapp Bot, with regex-callback routes (just like a web framework).  
(pratical extension of the examples on https://github.com/tgalal/yowsup)

# What it does?
- Basic messages and media download:  
![Example](http://i.imgur.com/pbuYCwO.jpg?1)  ![Example](http://i.imgur.com/liRRI1N.jpg?1)  
  
  
- Group administration:  
![Example](http://i.imgur.com/pSDCWDb.png?1)

- URL printscreen  
![Example](http://i.imgur.com/nCLjPD2.jpg?1)  
  
- Google Text to Speak  
![Example](http://i.imgur.com/X1ZhZip.jpg?1)

# Installation
1. Install the image handling system dependencies on ```bash opt/system-requirements.sh```
2. Create a virtualenv and install the requirements  ```pip install -r opt/requirements.pip```
3. Follow the instructions on ```src/config.py``` to get the whatsapp credentials.  
4. Then just run the server with  ```python src/server.py```  
