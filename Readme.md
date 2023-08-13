# House Scaper
This project allows you to collect information about the sale of apartments from the site https://rieltor.ua/flats-sale and saves it in json and csv extensions for further data editing if necessary <br />
There is a large amount of information on this site, and because of this, it was decided to make the script asynchronous and because of this, optimal speed is achieved.


## Start project
Use terminal to start project <br/>
All collected information is stored in the "data" folder, if it does not exist, it is automatically created <br/>


```bash
python main.py
```


## Possible errors
I use async requests, there is a chance to get banned on the site, so use a proxy
