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


class ExperimentHelper:
    """
    Helper used by the experiments.
    """
    @staticmethod
    def is_int(a):
        """Returns true if a is an integer"""
        try:
            int (a)
            return True
        except:
            return False

    @staticmethod
    def parse_parameter(param):
        """
        Parse a parameter.
        Can be a:b:c
            From a to b with step c
        Can be a,b,c
            Values a, b and c

        Returns a list of available values.

        Example:
            input: 0:1:.1
            output: (0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1)
        """

        if ":" in param:
            splitted = param.split(":")

            if ExperimentHelper.is_int(splitted[0]):
                start = int(splitted[0])
            else:
                start = float(splitted[0])

            if ExperimentHelper.is_int(splitted[1]):
                stop = int(splitted[1])
            else:
                stop = float(splitted[1])

            if ExperimentHelper.is_int(splitted[2]):
                step = int(splitted[2])
            else:
                step = float(splitted[2])

            return ExperimentHelper.frange(start,stop,step)

        if "," in param:
            split = param.split(",")
            ret  = list()
            for p in split:
                if ExperimentHelper.is_int(p):
                    ret.append(int(p))
                else:
                    ret.append(float(p))
            return ret

        ret = list()
        if ExperimentHelper.is_int(param):
            ret.append(int(param))
        else:
            ret.append(float(param))

        return ret

    @staticmethod
    def frange(start, end=None, inc=None):
        #"A range function, that does accept float increments..."

        if end is None:
            end = start + 0.0
            start = 0.0

        if inc is None:
            inc = 1.0

        L = []
        while 1:
            next = start + len(L) * inc
            if inc > 0 and next >= end:
                break
            elif inc < 0 and next <= end:
                break
            L.append(next)

        return L