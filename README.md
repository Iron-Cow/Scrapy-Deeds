## Task 
* scrap DEEDS from http://www.tauntondeeds.com/Searches/ImageSearch.aspx submitted in current year
* use Scrapy

### For project launch:
* Clone
* pip install requirements.txt (or pip3 install requirements.txt)
* scrapy crawl tauntondeeds -o deeds_result.json 
* check the new file 'deeds_result.json'


### Required fields
* date: datetime 
* type: str 
* book: str 
* page_num: str 
* doc_num: str 
* city: str 
* description: str 
* cost: float 
* street_address: str 
* state: str 
* zip: str