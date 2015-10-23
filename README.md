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
![Example](http://i.imgur.com/fItWbTR.jpg?1)
  
  
- Group administration  
![Example](http://i.imgur.com/pSDCWDb.png?1)  
and a bit more...
  


# Installation
1. Install the image handling system dependencies on ```bash opt/system-requirements.sh```
2. Create a virtualenv and install the requirements  ```pip install -r opt/requirements.pip```
3. Follow the instructions on ```src/config.py``` to get the whatsapp credentials.  
4. Then just run the server with  ```python src/server.py```  

To create your own views, check the ```src/router.py```, and the ```src/view/basic_views.py``` for a simple example.

