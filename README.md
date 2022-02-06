# New Taipei City-Building-Management-Information-Web-Crawler

# General

This project is my web crawler practice. It can help you get all building license from New Taipei City Building Management and save to NoSQL database (MongoDB) automatically. 

[建管系統便民服務資訊網](https://building-management.publicwork.ntpc.gov.tw/)

# ****Setup****

1. Set the environment.
    1. Anaconda
    2. Install WebDriver base on your web browser, I’m using chrome as my default web browser.
    3. Find out the most suitable verification image screenshot based on your screen. My screen is 24 inches so I set the screenshot range as [420:460,420:520] at function `img_process`.  
    4. Install package below.
    
    ```python
    beautifulsoup4==4.9.3
    ddddocr==1.1.0
    numpy==1.21.4
    opencv==4.5.3
    pandas==1.1.3
    pillow==8.4.0
    pip==20.2.4
    pymongo==3.12.1
    regex==2021.11.10
    requests==2.24.0
    selenium==4.1.0
    urllib3==1.26.7
    ```
    
2. Run the [main.py](http://main.py) code.
3. And you will get the whole New Taipei City building license🙂.
