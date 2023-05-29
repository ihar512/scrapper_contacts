# Scrapper Contacts Project Readme

## INITIAL ENVIRONMENT SETUP
1. Setup virtual environment for better package management:
   * Create virtual environment `python3 -m venv venv_ubuntu`
   * Activate `source env/bin/activate`
   * Use requirements file to install packages `python3 -m pip install -r requierments.txt`
2. Downlaod and install geckodriver
   1. Go to the geckodriver releases page (https://github.com/mozilla/geckodriver/releases). Find the latest version of the driver for your platform and download it. For example: `wget https://github.com/mozilla/geckodriver/releases/download/v0.32.0/geckodriver-v0.32.0-linux64.tar.gz`
   2. Extract the file with tar command: `tar -xvzf geckodriver*`
   3. Make it executable: `chmod +x geckodriver`
   4. Move files to /usr/local/bin/ path to easily access: `sudo mv geckodriver /usr/local/bin/`


## REFERENCES
https://scrapy.org/

https://trd.stage-directions.com/
https://plsn.com/#

Web scraping to extract contact information— Mailing Lists
https://medium.com/@rodrigonader/web-scraping-to-extract-contact-information-part-1-mailing-lists-854e8a8844d2
