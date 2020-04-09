from datetime import datetime
import scrapy
import re

# Year actualizer
CURRENT_YEAR = datetime.now().strftime("%Y")


class TauntonDeeds(scrapy.Spider):
    """tauntondeeds.com apartments spider"""

    name = "tauntondeeds"
    start_urls = ["http://www.tauntondeeds.com/Searches/ImageSearch.aspx", ]

    def format_row_data(self, row: scrapy.Selector) -> dict:
        """
        Handling of each row of page table
        :param row: response.css of the row
        :type row: scrapy.Selector
        :return: Dictionary for save
        :rtype: dict
        """

        fields = ["date",
                  "type",
                  "book",
                  "page_num",
                  "doc_num",
                  "city", ]

        regular_data = {el: row.css(f"td:nth-child({i + 2})::text").get().strip() or None for (i, el)
                        in enumerate(fields)}

        description_full = row.css("td:nth-child(8) span::text").get()
        sample = re.compile(r"^(LOT [0-9A-Z]+)?|(LOTS [0-9 &]+)? ?(SP \d+-\w)?(.* [0-9-]+)[A-Z ,]+(\$(\d+\.00))?")
        groups = sample.split(description_full)
        state = re.findall(r'(STATE \w*)', description_full)

        regular_data['date'] = datetime.strptime(regular_data['date'], '%m/%d/%Y')
        regular_data['description'] = " ".join(i for i in [groups[1], groups[9], groups[10]] if i) or None
        regular_data['cost'] = float(groups[13]) if groups[13] else None
        regular_data['street_address'] = groups[11].strip() if groups[11] else None
        regular_data['state'] = state[0][6:] if state else None
        regular_data['zip'] = groups[10].strip()[3:] if groups[10] else None

        return regular_data  # row result

    def get_rows(self, response: scrapy.FormRequest) -> dict:
        """
        Manages each row of page and pass it to new function
        :param response: Page
        :type response: scrapy.FormRequest
        :return: Dictionary for save
        :rtype: dict
        """

        # Each row handling
        for table_row in response.css('#ctl00_cphMainContent_gvSearchResults '
                                      'tr.gridRow, #ctl00_cphMainContent_'
                                      'gvSearchResults tr.gridAltRow'):
            yield self.format_row_data(table_row)

    def get_pages(self, response: scrapy.FormRequest) -> scrapy.FormRequest:
        """
        Manages the multiple pages for bigger queries
        :param response: Page
        :type response: scrapy.FormRequest
        :return: concrete page FormRequest
        :rtype: scrapy.FormRequest
        """

        # Pagination row
        paginator = response.css("#ctl00_cphMainContent_gvSearchResults tr.gridPager:first-child td table tr td")

        # Multi-pages with 'Last' problem (more than paginator length) /// solved
        pg = 0
        while int(paginator.css("a::text")[-1].extract()) != pg:
            pg += 1
            yield scrapy.FormRequest(
                url=response.url,
                formdata={
                    "ctl00_cphMainContent_txtLCSTartDate_dateInput_text":
                        f"1/1/{CURRENT_YEAR}",
                    "ctl00_cphMainContent_txtLCEndDate_dateInput_text":
                        f"12/31/{CURRENT_YEAR}",
                    "ctl00$cphMainContent$ddlLCDocumentType$vddlDropDown":
                        "101627",
                    '__VIEWSTATE': response.css(
                        'input#__VIEWSTATE::attr(value)'
                    ).extract_first(),
                    '__EVENTARGUMENT': f"Page${pg}",
                    "__EVENTTARGET": "ctl00$cphMainContent$gvSearchResults",
                }, callback=self.get_rows)

    def parse(self, response: scrapy.Request) -> scrapy.FormRequest:
        """
        Start scraping for all pages / rows
        :param response: Page
        :type response: scrapy.Request
        :return: Page request
        :rtype: scrapy.FormRequest
        """

        yield scrapy.FormRequest(
            url=response.url,
            formdata={
                "ctl00$cphMainContent$txtLCEndDate$dateInput":
                    f"{CURRENT_YEAR}-12-31-00-00-00",
                "ctl00$cphMainContent$txtLCSTartDate$dateInput":
                    f"{CURRENT_YEAR}-01-01-00-00-00",
                "ctl00$cphMainContent$ddlLCDocumentType$vddlDropDown":
                    "101627",
                "ctl00$cphMainContent$btnSearchLC": "Search Land Court",
                '__VIEWSTATE': response.css(
                    'input#__VIEWSTATE::attr(value)'
                ).extract_first(),
            }, callback=self.get_pages)
