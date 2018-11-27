import unittest
import fireeyeapicms.client as cli
import fireeyeapicms.resource as resources
import fireeyeapicms.utility as util
import json
import time

import os
USER=os.environ["USERNAME"]
PASSWORD = os.environ["PASSWORD"]
SERVER=os.environ["SERVER"]
SENDER=os.environ["SENDER"] #email address
SEARCH_DATE=os.environ["SEARCH_DATE"] # mm/dd/yyyy

class RequestError(Exception):
    def __init__(self,msg):
        super(RequestError,self).__init__()
        self.message=msg


class Login(unittest.TestCase):
    def test_login(self):
        client=cli.FireClient(USER,PASSWORD,SERVER,False)

    def test_search(self):
        """
        :param kwargs:
            num:
            sort:
            sort_by:
            offset:
            group_filter:
            applianaces:
            ---------------
            at least one of:
               "search[sender]",
               "search[recipient]",
               "search[subject_line]",
                "search[message_tracker_id]",
            ---------------
            optional:
                "search[start_date]",
                "search[end_date]",
                "search[chosen_label]",
        :return:
        """
        #todo(aj) make util package and SearchUtil class to do all this
        client = cli.FireClient(USER,PASSWORD,SERVER,False)
        resource = resources.SearchProcessed(client)
        kwargs = {}
        #kwargs["num"]="25"
        kwargs["search[start_date]"]=SEARCH_DATE
        kwargs["search[end_date]"]=SEARCH_DATE
        kwargs["search[sender]"]=SENDER
        #kwargs["search[subject_line]"]="Invoice 05469 from Artisanal Brewing Ventures"
        resource.search_url(kwargs=kwargs)
        total_time=13
        total_wait=0
        wait_inc = 1
        result = resource.request()
        result_json = result["data"]
        if result_json["job_status"]!="progress":
            raise RuntimeError("error:" + result["response"].status_code)

        result_resource = resources.SearchProcessed(client)
        result_resource.search_results(kwargs,result_json["job_id"])
        while total_wait < total_time:
            result = result_resource.request()
            if result["status"]=="Success":
                if result["data"]["job_status"]=="completed":
                    self.assertEqual(result["data"]["job_status"],"completed")
                    self.assertEqual(len(result["data"]["list"]),25)
                    pass
                    #handle data here
                    break
                else:
                    time.sleep(wait_inc)
                    total_wait+=wait_inc
            else:
                raise RuntimeError("error: " + result["response"].status_code)
        if total_wait >=total_time:
            raise RuntimeError("waited max time")

    def test_page(self):
        client = cli.FireClient(USER,PASSWORD,SERVER,False)
        search = util.SearchUtil(client,
                        num=20,
                        sender_address=SENDER,
                        start_date=SEARCH_DATE,
                        end_date=SEARCH_DATE)
        all_data = search.search()
        self.assertEqual(len(all_data),102)

    def test_default_page(self):
        client = cli.FireClient(USER,PASSWORD,SERVER,False)
        search = util.SearchUtil(client,
                        sender_address=SENDER,
                        start_date=SEARCH_DATE,
                        end_date=SEARCH_DATE)
        all_data = search.search()
        self.assertEqual(len(all_data),102)

    def test_no_results(self):
        client = cli.FireClient(USER,PASSWORD,SERVER,False)
        search = util.SearchUtil(client,
                        sender_address="xxxxx@xxxx.com",
                        start_date=SEARCH_DATE,
                        end_date=SEARCH_DATE)
        all_data = search.search()
        self.assertEqual(len(all_data),0)

if __name__ == "__main__":
    unittest.main()

