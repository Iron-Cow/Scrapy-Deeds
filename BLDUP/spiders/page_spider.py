from datetime import datetime
import scrapy
import re

CURRENT_YEAR = datetime.now().strftime("%Y")


class TauntonDeeds(scrapy.Spider):
    """tauntondeeds.com apartments spider"""

    name = "pages"
    start_urls = ["http://www.tauntondeeds.com/Searches/ImageSearch.aspx", ]

    def parse(self, response: scrapy.Request) -> scrapy.FormRequest:
        """
        Load the page with parameters for getting table size
        :param response: Object of page
        :type response: scrapy.Request
        :return: Content of page in scrapy.FormRequest object
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
                '__EVENTARGUMENT': f"Page$1",
                "__EVENTTARGET": "ctl00$cphMainContent$gvSearchResults",
            }, callback=self.format_row_data)

    def format_row_data(self, response) -> dict:
        last_pageg = response.css('#ctl00_cphMainContent_gvSearchResults '
                                  'tr.gridRow, #ctl00_cphMainContent_'
                                  'gvSearchResults tr.gridAltRow')
        last_page = last_pageg.css("td:nth-child(8) span::text").get()
        fields = ["date",
                  "type",
                  "book",
                  "page_num",
                  "doc_num",
                  "city",]
        regular_data = {el: last_pageg.css(f"td:nth-child({i+2})::text").extract_first().strip() or None for (i, el)
                        in enumerate(fields)}
        regular_data['date'] = datetime.strptime(regular_data['date'], '%m/%d/%Y')

        description = last_pageg.css("td:nth-child(8) span::text")[1].extract()

        regular_data['description'] = description
        mask = re.compile(r"^(LOT [0-9A-Z]+)?|(LOTS [0-9 &]+)? ?(SP \d+-\w)?(.* [0-9-]+)[A-Z ,]+(\$(\d+\.00))?")
        groups = mask.split(description)

        regular_data['zip'] = groups[10].strip()[3:] if groups[10] else None
        state = re.findall(r'(STATE \w*)', description)
        print(state)

        regular_data['state'] = state[0][6:] if state else None
        regular_data['street_address'] = groups[11].strip() if groups[11] else None
        print("=="*40)
        print(state)
        print(groups)
        print("=="*40)



        return {"Record": regular_data}
        #
        # desc = row.css("td:nth-child(8) span::text").get()
        #
        # mask = re.compile(r"^(LOT [0-9A-Z]+)?|(LOTS [0-9 &]+)? ?(SP \d+-\w)?(.* [0-9-]+)[A-Z ,]+(\$(\d+\.00))?")
        # groups = mask.split(desc)
        #
        # description = filter(len, map(
        #     lambda i: i.strip() if i is not None else "",
        #     (groups[1], groups[9], groups[10])
        # ))
        #
        # book = row.css("td:nth-child(4)::text").get().strip()
        # page_num = row.css("td:nth-child(5)::text").get().strip()
        #
        # return {
        #     "date": datetime.strptime(
        #         row.css("td:nth-child(2)::text").get(), "%m/%d/%Y"
        #     ),
        #     "type": row.css("td:nth-child(3)::text").get(),
        #     "book": book if book else None,
        #     "page_num": page_num if page_num else None,
        #     "doc_num": row.css("td:nth-child(6)::text").get(),
        #     "city": row.css("td:nth-child(7)::text").get(),
        #     "description": " ".join(description) if description else None,
        #     "cost": float(groups[13]) if groups[13] else None,
        #     "street_address": groups[11].strip() if groups[11] else None,
        #     "state": None,
        #     "zip": None,
        # }
