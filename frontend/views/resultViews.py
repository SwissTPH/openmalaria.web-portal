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

import json
from datetime import datetime
from django.utils import timezone
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.shortcuts import redirect
from frontend.models import experiment, simulationRun
from WorkerPackage.Task.tasks import runOpenMalaria
from frontend.views.generalViews import set_notification

class ResultsView(TemplateView):
    """
    ResultsView - where completed work (simulations) can be managed
    """
    #Template file this view requires
    template_name="results.html"

    def get_context_data(self, **kwargs):
        """
        Method populates the context with data needed for the template file to be rendered.
        """
        #Get the default context from the superclass.
        context = super(ResultsView, self).get_context_data(**kwargs)
        #Get the list of completed simulation groups for the currently logged in user.
        context['available_experiments'] = get_completed_experiments(self.request.user)
        #Return the context.
        return context

    def get(self, request, *args, **kwargs):
        """
        Handles HTTP GET requests. If request occurs via a URL, this method simply renders the ResultsView template.
        If request occurs via AJAX, then it returns a a lot of information about an experiment specified by 'experiment_id'. Note AJAX
        method requires a parameter named 'experiment_id' to be in the request or it will raise and exception and return code 400

        @param request: The http request object
        @param args: arguments
        @param kwargs: what else
        @return: Varies depending on the method used to access.
        """
        if request.is_ajax():
            #If the request is AJAX, then...
            try:
                #Retrieve the experiment object with an id = 'experiment_id' get parameter.
                exp = experiment.objects.get(id=request.GET['experiment_id'])
                #Fill out a JSON dictionary with the experiment information
                exp_data = {
                    'experiment_name':exp.name,
                    'experiment_description':exp.description,
                    'experiment_started': exp.created_on.strftime('%Y-%m-%d %H:%M:%S'),
                    'boinc': 'No',
                    'experiment_sim_count': len(exp.simulations.all())
                }
                if exp.use_boinc:
                    exp_data['boinc'] = 'Yes'

                #Fill out another JSON object for all simulation data regarding this experiment
                # Only do that if we have less than 200 simulations
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
                exp_data['experiment_sims'] = sim_data
                #return the data
                return HttpResponse(content=json.dumps(exp_data), content_type="application/json", status=200)
            except Exception as detail:
                #If an exception occurs, log it and return status 400
                print detail
                return HttpResponse(status=400)
        else:
            #If not an ajax request, just render the template
            return self.render_to_response(self.get_context_data(**kwargs))


def get_completed_experiments(current_user):
    """
    Method to get a list of experiments that have completed running (either complete, aborted, or failed).
    @param current_user: The user to get experiments for
    @return: A list of experiment objects
    """
    experiment_list = []
    try:
        #Get the list of user experiments that have been launched
        experiments = experiment.objects.filter(created_by = current_user, launched=True).order_by('-id')
        for exp in experiments:
           if exp.getStatus()["percentage_done"] == 100:
                experiment_list.append(exp)
    except Exception as detail:
        #if an exception occurred, print it to the log
        print detail
    #Return the list of completed experiments
    return experiment_list

#TODO add boinc capability here!
def relaunch_simulation(request, sim_id):
    """
    Method to relaunch an individual simulation from the results tab
    @param request: The HTTP request object
    @param sim_id: id of the simulation to be relaunched
    @return: nothing
    """
    if not request.is_ajax():
        #non-Ajax calls should be redirected to the results tab.
        return redirect('results')
    try:
        # Retrieve the simulation
        simulation = simulationRun.objects.get(id=sim_id)
        #reset it's status to 0
        simulation.status = 0
        simulation.start_time = datetime.now(tz=timezone.get_default_timezone())

        #reset it's finished status to false
        simulation.finished=False
        #clear the message
        simulation.message = ''
        #clear any results (should be none but just to be safe)
        simulation.sim_results = ''
        #launch the worker task
        result = runOpenMalaria.apply_async(args=[simulation.id], queue='openmalaria')
        #Set the Celery/RabbitMQ task id (so it can be canceled later)
        simulation.task_id = result.id
        #Save the changes
        simulation.save()
        #update the experiment group to be not finished as well (so it shows up in the dashboard)
        sim_exp = simulation.experiment
        sim_exp.finished = False
        sim_exp.save()

        #notify the user that everything went well
        set_notification('success','The simulation has been successfully relaunched!',request.session)
        #return a simple JSON object that says everything went ok so the javascript can handle the result appropriately
        return HttpResponse(content=json.dumps({'result':True}), content_type='application/json', status=200)
    except Exception as detail:
        #log the exception
        print detail
        #return a simple JSON object that says something didn't work so the javascript can handle the result appropriately
        return HttpResponse(content=json.dumps({'result':False}), content_type='application/json', status=200)
