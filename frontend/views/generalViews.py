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

from cStringIO import StringIO
from datetime import datetime
import json
import os
from shutil import rmtree
import tempfile
from django.contrib.auth import authenticate, login, logout
from django.contrib.sessions.models import Session
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import TemplateView
from OpenMalaria.settings import BOINC_HOST, BOINC_USER, BOINC_PASSWORD
from frontend.models import simulationRun, experiment
from frontend.objects.Helpers import zip_folder
from frontend.objects.Notification import Notification
from django.utils import timezone
from time import sleep
from frontend.boinc import BoincOpenmalaria
import gzip

def set_notification(notification_type,message,session):
    notification = Notification()
    notification.message = message
    notification.type = notification_type

    # Save in sessions
    if not session.__contains__("notifications"):
        session["notifications"] = set()

    session["notifications"].add(notification)


class DashboardView(TemplateView):
    #    simulations = {'name':'Name','list2':'Name'}
    template_name="dashboard.html"

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)
        #determine the active sessions
        context['active_sessions'] = getActiveSessionCount()
        user = self.request.user
        context['active_simulations'] = getActiveSimulationCount()
        context['pending_simulations'] = getPendingSimulationCount()
        #user = context['request']
        context['simulations'] = getUserSubmittedSimulations(user)
        context['experiments'] = getUserSubmittedExperiments(user)
        context['boinc_experiments'] = getUserSubmittedBoincExperiments(user)
        return context

def ajaxAuth(request):
    #Only handle ajax post requests, otherwise return an invalid header error
    if request.is_ajax() and request.method == "POST":
        userid = request.POST["uid"]
        password = request.POST["pwd"]
        user = authenticate(username=userid, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                nextPage = '/dashboard/'
                # TODO: This isn't quite working... fix it. This should auto redirect to the "next" page
                if 'next' in request.POST  and len(request.POST['next']) > 0:
                    nextPage = request.POST['next']
                response_data = json.dumps({'url': nextPage})
            else:
                response_data = json.dumps({'message':'Account disabled!'})
        else:
            response_data = json.dumps({'message':'Invalid username and/or password!'})
        return HttpResponse(content=response_data, content_type="application/json", status=200)
    else:
        return HttpResponse(status=400)

def performLogout(request):
    logout(request)

    return HttpResponseRedirect("/")



class HomeView(TemplateView):
    template_name="home.html"



def downloadExperimentBaseXML(request, experimentId):
    exp = experiment.objects.get(id=experimentId)
    expXML = exp.contents
    return HttpResponse(content=expXML, content_type="text/plain", status=200)


def downloadSimulationXML(request, simulationId):
    sim = simulationRun.objects.get(id=simulationId)
    simXML = sim.contents
    return HttpResponse(content=simXML, content_type="text/plain", status=200)

def downloadResults(request, simulationId):
    # Retrieve the results
    sim = simulationRun.objects.get(id = simulationId)

    file_content = sim.sim_results
    # Display them
    return HttpResponse(content=file_content, content_type="text/plain", status=200)

def downloadCtsout(request, simulationId):
    # Retrieve the ctsout
    sim = simulationRun.objects.get(id = simulationId)

    file_content = sim.sim_cts_out
    # Display them
    return HttpResponse(content=file_content, content_type="text/plain", status=200)

def downloadExperimentResults(request, experimentId):
    # Retrieve the experiment
    sleep(3) # need to sleep at least a second to prevent "dialog flash"
    exp = experiment.objects.get(pk=experimentId)

    # Create a temp directory
    dirpath = tempfile.mkdtemp()

    # Create the dir corresponding to the experiment
    experiment_dir = os.path.join(dirpath,'experiment'+str(experimentId))
    os.makedirs(experiment_dir)

    # Create the dir containing the scenarios
    scenarios_dir = os.path.join(experiment_dir,'scenarios')
    os.makedirs(scenarios_dir)

    # Create the dir containing the results
    results_dir = os.path.join(experiment_dir,'results')
    os.makedirs(results_dir)

    # Prepare the string that will represent the CSV file containing the mapping between scenarios and parameters
    parameterstate = 'scenario,'
    for param in exp.parameters.all():
        parameterstate += param.param_id+','

    # Strip the last ,
    parameterstate = parameterstate[:-1]
    parameterstate += "\n"

    # Fill it with the actual scenarios
    for run in exp.simulations.all():
        # Prepare the XML file path
        xml_path = os.path.join(scenarios_dir,str(run.id)+'.xml')
        # Create the XML file
        xmlfile = open(xml_path, 'w')
        xmlfile.write(run.contents)
        xmlfile.close()

        # Take the result (if present)
        if run.status == 100:
#            result_str = run.results.all()[0].file
            result_path = os.path.join(results_dir,str(run.id)+'.txt')
            result_file = open(result_path,'w')
#            result_file.write(result_str)
            result_file.write(run.sim_results)
            result_file.close()

            cts_path = os.path.join(results_dir,str(run.id)+'cts.out')
            cts_file = open(cts_path,'w')
            cts_file.write(run.sim_cts_out)
            cts_file.close()


        # Add to the parameterstate
        parameterstate+=str(run.id)+'.xml,'
        for param in run.parameters.all():
            parameterstate+=str(param.param_value)+','
        parameterstate = parameterstate[:-1]+"\n"

    # Create the mapping file
    mapping_path = os.path.join(experiment_dir,'mapping.csv')
    mapping_file = open(mapping_path,'w')
    mapping_file.write(parameterstate)
    mapping_file.close()

    # Create the description file
    description_path = os.path.join(experiment_dir,'description.txt')
    description_file = open(description_path, 'w')
    description_file.write('Name: %s\n' % exp.name)
    description_file.write('Description: %s\n' % exp.description)
    description_file.close()

    # Add the base XML
    base_path = os.path.join(experiment_dir,'base.xml')
    base_file = open(base_path,'w')
    base_file.write(exp.contents)
    base_file.close()

    # Create the zip
    # We are using a StringIO to stay in memory
    experiment_zip = StringIO()
    zip_folder(experiment_dir,experiment_zip)

    # Cleanup
    rmtree(dirpath)

    # Send the response

    response = HttpResponse(mimetype='application/zip')
    response.set_cookie('fileDownload',value='true',path='/')
    response['Content-Disposition'] = 'filename=Experiment'+experimentId+'.zip'
    response.write(experiment_zip.getvalue())
    return response




def getActiveSessionCount():
    return Session.objects.get_query_set().filter(expire_date__gte=datetime.now(tz=timezone.get_default_timezone())).count()

def getActiveSimulationCount():
    try:
        simulations_count = simulationRun.objects.all().exclude(status=0).exclude(status=-1).exclude(status=100).count()
        return simulations_count
    except Exception, e:
        print 'Exception occurred while trying to get active simulation count'
        print e
        return 0

def getPendingSimulationCount():
    try:
        simulations_count = simulationRun.objects.filter(status=0, launched=True, use_boinc=False).count()
        return simulations_count
    except Exception, e:
        print 'Exception occurred while trying to get pending simulation count'
        print e
        return 0

def getUserSubmittedSimulations(activeUser):

    try:
        simulations = simulationRun.objects.filter(user = activeUser, experiment = None, use_boinc=False).order_by('-id')
        return simulations
    except Exception, e:
        print 'Exception occurred while trying to get user submitted simulation objects'
        print e
        return None

def getUserSubmittedExperiments(activeUser):
    tmpExperiments = []
    try:
        experiments = experiment.objects.filter(created_by = activeUser, launched=True, use_boinc=False, finished=False).order_by('-id')
        for exp in experiments:
            if exp.getStatus()["percentage_done"] < 100:
                tmpExperiments.append(exp)

    except Exception, e:
        print 'Exception occurred while trying to get user submitted experiment objects'
        print e

    return tmpExperiments

def getUserSubmittedBoincExperiments(activeUser):
    tmpExperiments = []
    try:
        experiments = experiment.objects.filter(created_by = activeUser, launched=True, use_boinc=True, finished=False).order_by('-id')
        for exp in experiments:
            if exp.getStatus()["percentage_done"] < 100:
                tmpExperiments.append(exp)

    except Exception, e:
        print 'Exception occurred while trying to get user submitted boinc experiment objects'
        print e

    return tmpExperiments


def getUserSimulationStatus(request):
    if request.is_ajax() and request.method == "GET":
        results = {}
        sims = list()
        exps = list()
        user = request.user

        experiments = experiment.objects.filter(created_by = user,finished=False).order_by('-id')
        for exp in experiments:
            # Retrieve the experiment status
            status = exp.getStatus()

            # this is in progress experiment => store it
            exps.append({'id': exp.id, 'status': status})

            # Add the simulations as well if this is not a boinc experiment
            # and if the simulations are less than 200
            if not exp.use_boinc and status["total_simulations"] < 200:
                for sim in exp.simulations.all():
                    sims.append({'id':sim.id, 'status':sim.status, 'message':sim.message})

        # Store the experiments status
        results['exps'] = exps
        # And the sims status
        results['sims']= sims

        return HttpResponse(content=json.dumps(results), content_type="application/json", status=200)
    else:
        return HttpResponse(status=400)


def pollBoincJobs(request):
    engine = BoincOpenmalaria(BOINC_HOST,user=BOINC_USER, password=BOINC_PASSWORD)
    simulations = simulationRun.objects.filter(use_boinc = True, launched=True, status=0)
    for sim in simulations:
        status = engine.status(sim.task_id)
        if status == 1:
            sim.status = 100
            sim.finished = True
            results = engine.output(sim.task_id)
            if results is not None:
                fp = StringIO(results)
                gfp = gzip.GzipFile(fileobj=fp)
                sim.sim_results = gfp.read()
                gfp.close()
        else:
            sim.status = status
            sim.message = engine.error
        sim.save()
    return HttpResponse(content='Ok', content_type='text/html', status=200)
