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

from datetime import datetime
import json
from django.http import HttpResponse
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from django.shortcuts import redirect, render_to_response
from OpenMalaria.settings import BOINC_HOST, BOINC_PASSWORD, BOINC_USER, CELERY_BROKER
from frontend.models import scenario, scenarioParameter, experimentParameter, experiment, simulationRun, simulationRunParameter, additionalUserInfo
from frontend.objects.ExperimentHelper import ExperimentHelper
from frontend.views.generalViews import set_notification
from WorkerPackage.Task.tasks import runOpenMalaria
from django.utils import timezone
from django.db.models import Q
from celery.app import Celery
from xml.dom import minidom
from frontend.boinc import BoincOpenmalaria
from uuid import uuid4


def createSimulationsRuns(new_experiment):
    # 2 lists
    # a list containing the parameter "id"  like ('EIR', 'FunestusInfectiousness',etc)
    # another one containing the parameters possibilities like ((1,2,3), (4,5,6))

    if len(new_experiment.parameters.all()) == 0:
        run = simulationRun()
#        run.scenario_id = new_experiment.scenario.id
        run.user = new_experiment.created_by
        run.experiment = new_experiment
        run.use_boinc = new_experiment.use_boinc
        run.contents = new_experiment.contents
        run.save()
    else:
        param_ids = list()
        possibilities = list()
        param_desc = {}

        for param in new_experiment.parameters.all():
            param_ids.append(param.param_id)
            param_desc[param.param_id] = param.description
            possibilities.append(ExperimentHelper.parse_parameter(param.param_value))


        numPar = [len(i) for i in possibilities]
        # calculate total number of possibilities
        product = 0
        exec('product =' + '*'.join(map(str,numPar)))
        # generate list of lists of all possibilities
        combinations = []
        for i in range(product):
            t = i
            combinations.append([])
            for j in range(len(numPar)):
                combinations[i].append((possibilities[j][t%numPar[j]]))
                t //= numPar[j]

        #return combinations
        param_space = list()

        for param_list in combinations:
            param_state = dict()
            for i in range(len(param_list)):
                param_state[param_ids[i]] = param_list[i]
            param_space.append(param_state)



        for space in param_space:
            new_scenario = new_experiment.contents
            param_string_for_header = ''
            # Replace the different parameters inside
            for (param_name, param_value) in space.iteritems():
                new_scenario = new_scenario.replace("@%s@" % param_name,str(param_value))
                param_string_for_header += str(param_name)
                param_string_for_header += ':'
                param_string_for_header += str(param_value)
                param_string_for_header += ','

            dom = minidom.parseString(new_scenario)
            params = dom.getElementsByTagName('scenario')
            for param in params:
                name = param.getAttribute('name')
                name += ','+param_string_for_header
                param.setAttribute('name',name )

            # Create the simulation run
            run = simulationRun()
            #run.scenario_id = new_experiment.scenario.id
            run.user = new_experiment.created_by
            run.contents = dom.toxml()
            run.experiment = new_experiment
            run.use_boinc = new_experiment.use_boinc
            run.save()

            # Create the parameters
            for (param_name, param_value) in space.iteritems():
                param = simulationRunParameter()
                param.param_id = param_name
                param.description = param_desc[param_name]
                param.param_value = param_value
                param.simulationRun = run
                param.save()


def launchSimulationGroup(simulationGroup):
    try:
    # Launch all the runs
        if simulationGroup.use_boinc:
            engine = BoincOpenmalaria(BOINC_HOST,user=BOINC_USER, password=BOINC_PASSWORD)
            engine._debug = False
            for simulation_run in simulationGroup.simulations.all():
                simulation_run.task_id = 'ndom_'+str(simulation_run.id)+'_'+str(uuid4())
                if not engine.submit(simulation_run.task_id, simulation_run.contents):
                    print "Failed: %s" % engine.error
                else:
                    simulation_run.launched = True
                    simulation_run.start_time = datetime.now(tz=timezone.get_default_timezone())
                simulation_run.save()
        else:
            for simulation_run in simulationGroup.simulations.all():
                task = runOpenMalaria.apply_async(args=[simulation_run.id], queue='openmalaria')
                simulation_run.task_id = task.id
                simulation_run.start_time = datetime.now(tz=timezone.get_default_timezone())
                simulation_run.launched = True
                simulation_run.save()
        # Launch it on the DB
        simulationGroup.launched = True
        simulationGroup.save()
        return True
    except Exception as detail:
        print detail
        return False


class ExperimentView(TemplateView):
    """
    Home view.
    """
    template_name="experiments.html"

    def get_context_data(self, **kwargs):
        context = super(ExperimentView, self).get_context_data(**kwargs)
        context["experiment_objects"] = experiment.objects.all().filter(created_by = self.request.user).exclude(launched = True)
        return context

    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            exp = experiment.objects.get(id=request.GET['current_experiment'])
            if exp is not None:
                json_exp_data = {
                    'name':exp.name,
                    'description':exp.description,
                    'user': exp.created_by.username,
                    'date': exp.created_on.strftime("%Y-%m-%d %H:%M:%S"),
                    'content': exp.contents,
                    'boinc': 'No'
                }
                if exp.use_boinc:
                    json_exp_data['boinc'] = 'Yes'

                params = dict()
                params_in_scenario = dict()
                for param in exp.parameters.all():
                    params[param.description] = ExperimentHelper.parse_parameter(param.param_value)
                    params_in_scenario[param.description] = param.param_id
                json_exp_data["parameters"] = params
                json_exp_data["params_in_scenario"] = params_in_scenario
                json_exp_data['experiment_sim_count'] = len(exp.simulations.all())

                sim_data = {}
                for sim in exp.simulations.all():
                    #describe the status of the simulation
                    sim_info = {
                        'sim_status':sim.status,
                        'sim_message':sim.message
                    }
                    #describe the parameters of the simulation
                    sim_parameters={}
                    for param in sim.parameters.all():
                        sim_parameters[param.description+' (@'+param.param_id+'@)'] = param.param_value
                        #add the parameter info to the simulation info
                    sim_info['parameters'] = sim_parameters
                    #add this simulation information to the simulation data object (dictionary of all simulations)
                    sim_data[sim.id] = sim_info
                    #Add simulation data to the experiment dictionary
                json_exp_data['experiment_sims'] = sim_data
                response_data = json.dumps(json_exp_data)
            else:
                response_data = json.dumps({'message':'Invalid scenario request!'})
            return HttpResponse(content=response_data, content_type="application/json", status=200)
        else:
            return self.render_to_response( self.get_context_data(**kwargs) )

    def post(self, **kwargs):
        return self.render_to_response( self.get_context_data(**kwargs) )

class ExperimentCreateView(TemplateView):
    template_name="experimentCreate.html"
    def get_context_data(self, **kwargs):
        context = super(ExperimentCreateView, self).get_context_data(**kwargs)
        context["scenario_objects"] = scenario.objects.filter(Q(created_by = self.request.user)|Q(is_public = True)).order_by('-id')
        context['max_sim_count']  = additionalUserInfo.objects.get(user=self.request.user).max_sims
        return context


    def post(self, request):
        try:
            # Retrieve the form info
            currentScenarioId = request.POST["current_scenario"]
            experimentName = request.POST["new_experiment_name"]
            experimentDesc = request.POST["new_experiment_description"]
            theParams = request.POST["parameters"]
            jsonParams = json.loads(theParams)
            experimentParams = jsonParams["parameters"]

            # Create the experiment object
            new_experiment = experiment()
#            new_experiment.scenario_id = currentScenarioId
            new_experiment.name = experimentName
            new_experiment.description = experimentDesc
            new_experiment.created_by = request.user
            new_experiment.created_on = datetime.now(tz=timezone.get_default_timezone())
            new_experiment.contents = scenario.objects.get(id=currentScenarioId).contents

            if request.POST.get('use_boinc') is not None:
                new_experiment.use_boinc = True

            new_experiment.save()
            # Create the parameters
            for param in experimentParams:
            #                param_id = param['param_id']
                uid = param['id']
                param_val = param['value']
                configParam = experimentParameter()
                scenarioParam = scenarioParameter.objects.get(id = uid)
                configParam.param_id = scenarioParam.param_id
                configParam.description = scenarioParam.description
                configParam.param_value = param_val
                configParam.experiment =  new_experiment
                configParam.save()

            createSimulationsRuns(new_experiment)

            if request.POST["should_execute_experiment"] == "1": #true, should launch experiment
                if launchSimulationGroup(new_experiment):
                    set_notification('success','The experiment has been launched successfully!',request.session)
                    return redirect('dashboard')
                else:
                    set_notification('error', 'Failed to launch experiment',request.session)
                    return redirect('experiments')
            else:
                set_notification('success', 'The experiment was successfully saved for later execution', request.session )
                return redirect('experiments')

        except Exception as detail:
            print 'Error saving experiment configuration'
            print detail
            set_notification('error','There was an error trying to save your configuration!',request.session)
            return redirect('experiments')


class ExperimentDuplicateView(TemplateView):
    template_name="experimentDuplicate.html"

    def get_context_data(self, **kwargs):
        context = super(ExperimentDuplicateView, self).get_context_data(**kwargs)
        return context

    def get(self, request, *args, **kwargs):
        old_exp = experiment.objects.get(id=kwargs['experiment_id'])
        max_sims = additionalUserInfo.objects.get(user=request.user).max_sims
        new_context = RequestContext(request, {'experiment': old_exp, 'max_sims': max_sims})
        return render_to_response('experimentDuplicate.html', context_instance=new_context)

    def post(self, request):
        try:
            # Retrieve the form info
            oldExperimentId = request.POST["old_experiment_id"]
            experimentName = request.POST["new_experiment_name"]
            experimentDesc = request.POST["new_experiment_description"]
            theParams = request.POST["parameters"]
            jsonParams = json.loads(theParams)
            experimentParams = jsonParams["parameters"]
            oldExperiment = experiment.objects.get(id=oldExperimentId)
            # Create the experiment object
            new_experiment = experiment()

            if request.POST.get('use_boinc') is not None:
                new_experiment.use_boinc = True

            # new_experiment.scenario_id = oldExperiment.scenario_id
            new_experiment.contents = oldExperiment.contents
            new_experiment.name = experimentName
            new_experiment.description = experimentDesc
            new_experiment.created_by = request.user
            new_experiment.created_on = datetime.now(tz=timezone.get_default_timezone())
            new_experiment.save()
            # Create the parameters
            for param in experimentParams:
                uid = param['id']
                param_val = param['value']
                configParam = experimentParameter()
                expParam = experimentParameter.objects.get(id = uid)
                configParam.param_id = expParam.param_id
                configParam.description = expParam.description
                configParam.param_value = param_val
                configParam.experiment =  new_experiment
                configParam.save()

            createSimulationsRuns(new_experiment)

            if request.POST["should_execute_experiment"] == "1": #true, should launch experiment
                if launchSimulationGroup(new_experiment):
                    set_notification('success','The duplicated experiment has been launched successfully!',request.session)
                    return redirect('dashboard')
                else:
                    set_notification('error', 'Failed to launch duplicated experiment',request.session)
                    return redirect('experiments')
            else:
                set_notification('success', 'The experiment was successfully duplicated and saved for later execution', request.session )
                return redirect('experiments')

        except Exception as detail:
            print 'Error saving experiment configuration'
            print detail
            set_notification('error','There was an error trying to save your configuration!',request.session)
            return redirect('experiments')


def deleteSimulationGroup(request,experiment_id):
    # Retrieve the experiment
    exp = experiment.objects.get(pk=experiment_id)

    # Delete the experiment
    exp.delete()

    set_notification('success','The simulation group has been deleted.',request.session)
    return redirect('results')

def deleteExperimentGroup(request,experiment_id):
    # Retrieve the experiment
    exp = experiment.objects.get(pk=experiment_id)

    # Delete the experiment
    exp.delete()

    set_notification('success','The simulation group has been deleted.',request.session)
    return redirect('experiments')



@csrf_exempt
def launchExperiment(request):
    if not request.method == "POST" or request.POST["experiment_launch_id"] is None :
        return redirect('experiments')

    # Retrieve the experiment
    experiment_id = request.POST["experiment_launch_id"]
    exp = experiment.objects.get(pk=experiment_id)

    if launchSimulationGroup(exp):
        if exp.use_boinc:
            set_notification('success','The experiment has been launched on the BOINC system successfully!',request.session)
        else:
            set_notification('success','The experiment has been launched on the compute cluster successfully!',request.session)
        return redirect('dashboard')
    else:
        set_notification('error', 'Failed to launch experiment',request.session)
        return redirect('experiments')


def defineExperiment(request):
    if request.is_ajax() and request.method == "GET" and request.GET["current_scenario"] is not None:
        currentScenarioId = request.GET["current_scenario"]
        scenarioParams = scenarioParameter.objects.all().filter(scenario_id = currentScenarioId).order_by('-id')
        array_data = []
        for parameter in scenarioParams:
            dict = {}
            dict['id'] = parameter.id
            dict['param_id'] = parameter.param_id
            dict['default_value'] = parameter.default_value
            dict['description'] = parameter.description
            array_data.append(dict)

        response_data = {}
        response_data['items']=array_data
        #response_data['contents'] = scenarioUpload.objects.get(id = currentScenarioId).contents
#        print >>sys.stderr, response_data
        return HttpResponse(content=json.dumps(response_data), content_type="application/json", status=200)
    else:
        return redirect('experiments')


def cancelRun(request,runid):
    # Retrieve the run
    run = simulationRun.objects.get(pk = runid)

    # Cancel the task
    celery = Celery('celeryOpenmalaria', backend='amqp',broker= CELERY_BROKER)
    celery.control.revoke(run.task_id,terminate=True)
    # Cancel it in the DB
    run.status = -1
    run.message = 'Cancelled by user.'
    run.save()
    return HttpResponse(content=json.dumps({'status': 'canceled'}), content_type="application/json", status=200)
    #changed to use ajax.
    #return redirect('dashboard')


def downloadScenarioXML(request, run_id):
    # Retrieve the run
    run = simulationRun.objects.get(pk=run_id)

    response = HttpResponse(mimetype='application/xml')
    response.write(run.contents)
    response['Content-Disposition'] = 'filename=scenario_'+run_id+'.xml'
    return response



