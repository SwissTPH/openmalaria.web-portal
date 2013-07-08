"""
    Copyright (C) 2012-2013 Center for Research Computing, University of Notre Dame
    Initially developed by Gregory Davis <gdavis2@nd.edu>, Benoit Raybaud <Benoit.Raybaud.1@nd.edu>, Alexander Vyushkov
    <Alexander.Vyushkov@nd.edu>, and Cheng Liu <Cheng.Liu.125@nd.edu>.

    Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
    documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
    rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
    permit persons to whom the Software is furnished to do so, subject to the following conditions:

    1. The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
    Software.

    2. Neither the name of the University of Notre Dame, nor the names of its contributors may be used to endorse or
    promote products derived from this software without specific prior written permission.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
    WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS
    OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
    OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

#    Python connector for openmalaria BOINC server on malariacontrol.net
import requests
from OpenMalaria.settings import BOINC_HOST, BOINC_PASSWORD, BOINC_USER


__version__ = '0.1.0a'

class BoincOpenmalaria:

    def __init__(self, url, user=None, password=None, application="openmalaria"):
        self._url = url
        self.error = ""
        self._debug = None
        self.user = user
        self.jobstatus = None
        self.password = password
        self.application = application

    def __str__(self):
        """  The informal string representation of BoincOpenmalaria object
        Called by the str() built-in function and by the print statement to compute
         the "informal" string representation of an object.
        This differs from __repr__() in that it does not have to be a valid Python
        expression: a more convenient or concise representation may be used
        instead. The return value must be a string object.
        @return: Description of an object
        """
        if self.user is not None:
            url = "%s:%s@%s" % (self.user, self.password, self._url)
        else:
            url = self._url

        return "BoincOpenmalaria: %s (%s)" % (url, self.error)

    def __repr__(self):
        """ This __repr__ implementation  just calls __str__
        Called by the repr() built-in function and by string conversions (reverse
        quotes) to compute the  "official" string representation of an object. If at all
        possible, this should look like a valid Python expression that could be used
        to recreate an object with the same value (given an appropriate environment).
        If this is not possible, a string of the form <...some useful description...>
         should be returned. The return value must be a string object. If a class
         defines __repr__() but not __str__(), then __repr__() is also used when an
         "informal" string representation of instances of that class is required.

        This is typically used for debugging, so it is important that the representation
        is information-rich and unambiguous.

        @return: Description of an object
        """
        return self.__str__()

    def _post(self, script, data):
        """ Internal wrapper for requests.post function

        @param script: Endpoint to be called. Initial part of URL is taken from self._url
        @param data: data to be sent in POST request. Passes directly to requests.post function
        @return:
            Body of http response
            None if status code is not 200
        """


#        if self._debug:
#            data["debug"] = "internal"

        try:

            r = requests.post("%s/%s" % (self._url, script), data=data, auth=(self.user, self.password))
        except requests.exceptions.RequestException as err:
            self.error = "%s" % err
            return None

        if self._debug:
            print self.user,self.password

        if r.status_code != 200:
            self.error = "Status Code: %s" % r.status_code
            return None

        return r

    def submit(self, wu_name, xml):
        """ Submit new job to BOINC server
        @param wu_name: workunit name
        @param xml: XML file for OpenMalaria
        @return:
            True if job was submitted successfully
            False if job submission failed
        """

        payload = {'wu_name': wu_name,
                         'xml': xml,
                         'appname':self.application}
        r = self._post("openmalaria_submit.php", data=payload)

        if r is None:
            return False

        if self._debug is not None:
            print "Response: %s \n" % r.text
            #print "JSON: %s \n" % r.json()

        # json property (requests v0.14.2) was replaced with json() function (v1.1.0)
        if requests.__version__.split('.')[0] != '0':
            self.error = r.json()["message"]
            result = r.json()["result"]
        else:
            self.error = r.json["message"]
            result = r.json["result"]

        if result == "ok":
            return True

        return False

    def status(self, wu_name):
        """ Check status of a job submitted by submit function

        @param wu_name: workunit name
        @return:
            "-1 If error occurs
            0 if job isn't done yet
            1 if job is done
            2 if job failed
        """
        payload = {'wu_name': wu_name}
        r = self._post("openmalaria_get_status.php", data=payload)
        if r is None:
            return 0

        # json property (requests v0.14.2) was replaced with json() function (v1.1.0)
        if requests.__version__.split('.')[0] != '0':
            self.jobstatus = r.json()["result"]
            self.error  = r.json()["message"]
        else:
            self.jobstatus = r.json["result"]
            self.error  = r.json["message"]


        if self.jobstatus == "done":
            return 1

        if self.jobstatus == "fail" or self.jobstatus == "done-deleted":
            return -1

        if self.jobstatus == "notdone" or self.jobstatus == "error":
            return 0

        return -1


    def output(self, wu_name):
        """ Get output from a job submitted by submit function

        @param wu_name: workunit name
        @return:
                Output from OpenMalaria process
                None is error occurs
        """
        payload = {'wu_name': wu_name}
        r = self._post("openmalaria_get_output.php", data=payload)
        if r is None:
            return None
        return r.content

    def cancel(self, wu_name):
        """ Cancel BOINC job identified by wu_name

        @param wu_name: workunit name
        @return: True if job was cancelled successfully
        False if job wasn't cancelled
        """
        payload = {'wu_name': wu_name}
        r = self._post("openmalaria_cancel.php", data=payload)
        if r is None:
            return False

        # json property (requests v0.14.2) was replaced with json() function (v1.1.0)
        if requests.__version__.split('.')[0] != '0':
            result = r.json()["result"]
            message = r.json()["message"]
        else:
            result = r.json["result"]
            message = r.json["message"]

        if result == "ok":
            return True

        self.error  = message
        return False

if __name__ == "__main__":
    engine = BoincOpenmalaria(BOINC_HOST,user=BOINC_USER, password=BOINC_PASSWORD)
    engine._debug = True
    f = open("single.xml")
    xml = f.read()
    f.close()

    if engine.submit("openmalaria_26", xml=xml):
        print "Ok"
    else:
        print "Failed: %s" % engine.error



    print engine.jobstatus("openmalaria_23")
    #print engine.output("openmalaria_23")
