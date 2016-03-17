# whatsapp-bot-seed
A small python seed to create a Whatsapp Bot, with regex-callback routes (just like a web framework).  
(practical extension of the examples on https://github.com/tgalal/yowsup)

# What it does?
- Basic message handling:  
![Example](http://i.imgur.com/TbirVKg.jpg?1)  
  
  
  
- Automatic media (images and videos) download, and url print screens  
![Example](http://i.imgur.com/fItWbTR.jpg?1)  

  
  
- Youtube Video Downloads, and Text to Speech  
![Example](http://i.imgur.com/dMbWLCm.jpg?1)  

  
  
- Google image and web search  
![Example](http://i.imgur.com/gDYIEej.jpg?1)
  
  
- Group administration  
![Example](http://i.imgur.com/pSDCWDb.png?1)  
and a bit more...
  


# Installation
1. Install the image handling system dependencies on ```bash opt/system-requirements.sh```
2. Create a virtualenv and install the requirements  ```pip install -r opt/requirements.pip```
3. Follow the instructions on ```src/config.py``` to get the whatsapp credentials.  
4. Then just run the server with  ```python src/server.py```  

# Or with Docker!
$ git clone https://github.com/joaoricardo000/whatsapp-bot-seed/  
$ cd whatsapp-bot-seed  
*(Edit Dockerfile to include your credentials)*  
$ docker build -t whatsapp-bot .  
$ docker run -p 0.0.0.0:9005:9005 whatsapp-bot  

The server will be running. Access http://localhost:9005 (default: admin:password) for process controll and logs.


#### To create your own views, check out ```src/router.py``` and ```src/view/basic_views.py``` for examples.

