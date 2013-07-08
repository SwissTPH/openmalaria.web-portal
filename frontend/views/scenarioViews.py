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

import json, re, os, time, subprocess
from datetime import datetime
from django.http import HttpResponse
from django.shortcuts import redirect, render_to_response
from django.views.generic import TemplateView
from frontend.models import scenario, scenarioParameter, additionalUserInfo
from frontend.views.generalViews import set_notification
from django.views.decorators.csrf import csrf_exempt
from django.template import RequestContext
from django.utils import timezone
from django.db.models import Q

########################################################################################################################
# IMPORTANT!
# This file contains ONLY the methods and objects necessary to implement all of the functionality for the
# 'Manage Scenarios' tab. All other functionality should be implemented elsewhere!
########################################################################################################################

########################################################################################################################
# Class-based view for the scenarios tab
class ScenarioView(TemplateView):
    template_name="scenarios.html"

    def get_context_data(self, **kwargs):
        """
        Returns context-specific variables to be used in rendering the template.
        """
        context = super(ScenarioView, self).get_context_data(**kwargs)
        # Create a list (newly created first) of scenario objects that are owned by current user or publicly available.
        context["scenario_objects"] = scenario.objects.filter(Q(created_by=self.request.user)|Q(is_public = True)).order_by('-id')
        context["can_post_public"] = additionalUserInfo.objects.get(user_id=self.request.user.id).post_public
        return context

    # If the get request is ajax, it will return a json object with details about a specific scenario, otherwise
    # It just returns basic information about all scenarios (name) to populate the scenario list
    def get(self, request, *args, **kwargs):
        """
        Handles the general view (when non-ajax) or gets information about a particular scenario (when ajax)
        """
        if request.is_ajax():
            # since it's ajax, we assume the user wants information and has passed in the scenario id of interest in "current_scenario" field
            upload = scenario.objects.get(id=request.GET.get('current_scenario'))
            # if the scenario id is valid, then try to return a JSON object with relevant information. Otherwise, show an error.
            if upload is not None:
                # begin with the assumption that this scenario can be deleted/edited
                can_modify = True
                # If the current user did not create the scenario, then it cannot be deleted/edited
                if upload.created_by != request.user:
                    can_modify = False

                # build the dictionary of information to return
                infoDictionary = {}
                infoDictionary['name'] = upload.name
                infoDictionary['description'] = upload.description
                infoDictionary['user'] = upload.created_by.username
                infoDictionary['date'] = upload.created_on.strftime('%Y-%m-%d %H:%M:%S')
                infoDictionary['modified'] = upload.modified_on.strftime('%Y-%m-%d %H:%M:%S')
                infoDictionary['contents'] = upload.contents
                infoDictionary['can_modify'] = can_modify
                infoDictionary['is_public'] = upload.is_public

                params = dict()
                params_in_scenario = dict()
                for param in upload.parameters.all():
                    params[param.description] = param.default_value
                    params_in_scenario[param.description] = param.param_id
                infoDictionary['parameters'] = params
                infoDictionary['params_in_scenario'] = params_in_scenario

                response_data = json.dumps(infoDictionary)
            else:
                response_data = json.dumps({'message':'Invalid scenario request!'})
            # send the result (error or info dictionary) back to the user
            return HttpResponse(content=response_data, content_type='application/json', status=200)
        else:
            # if it's not an ajax request, assume show the standard scenario view
            return self.render_to_response( self.get_context_data(**kwargs) )


########################################################################################################################
# Class-based view for the scenario creation page
class ScenarioCreateView(TemplateView):
    template_name="scenarioCreate.html"
    def get_context_data(self, **kwargs):
        context = super(ScenarioCreateView, self).get_context_data(**kwargs)
        context["can_post_public"] = additionalUserInfo.objects.get(user_id = self.request.user.id).post_public
        return context

    def post(self, request, **kwargs):
        """
        Handles the uploading of new scenario XML files
        """
        # Create a new scenarioUpload object
        upload = scenario()
        # Add properties based on request parameters. Note: .get used to prevent exception if parameter is not in request
        upload.name = request.POST.get('new_scenario_name')
        upload.description = request.POST.get('new_scenario_description')
        upload.contents = request.FILES.get('new_scenario_file').read()
        upload.is_public = 'new_scenario_public' in request.POST

        should_validate = 'new_scenario_validate' in request.POST

        if should_validate:
            #validate xml schema from OpenMalaria
            output = ''+validateScenarioUploadContents(upload.contents)
            if len(output) > 0:
                #if there was any error, the length will be greater than 0... put the error in a notification and render self.
                set_notification('error','<p>The following error(s) occurred:</p><p>'+output+'</p><p>The scenario was not saved. Correct the error(s) listed above and try again.</p>', request.session)
                return self.render_to_response( self.get_context_data(**kwargs) )


        # Check to see if there are any variables that need to be specified
        regex = re.compile('"@(.*?)@"')
        variables = regex.findall(upload.contents)



        if variables:
            # If this scenario has variables, then forward this info to another page where they can be specified. DO NOT SAVE UPLOAD HERE!
            # This is saved via the DefineScenarioParams method below
            req_params = {}
            req_params['name'] = upload.name
            req_params['description'] = upload.description
            req_params['contents'] = upload.contents
            req_params['is_public'] = upload.is_public
            req_params['params'] = variables
            return render_to_response('scenarioParams.html', req_params, context_instance = RequestContext(request) )

        # TODO: validate these parameters. Assuming the name,description,and contents are always present (javascript front-end validation used)



        # Mark the provenance of the upload
        upload.created_on = datetime.now(tz=timezone.get_default_timezone())
        upload.modified_on = upload.created_on
        upload.created_by = request.user
        # Save to the database
        upload.save()
        # show success message and render the template
        set_notification('success','Success!', request.session)
        return redirect('scenarios')

########################################################################################################################
def deleteScenario(request,scenario_id):
    """
    Handles deleting scenarioUpload objects
    """
    # Get the scenario and delete it
    upload = scenario.objects.get(id=scenario_id)
    upload.delete()
    set_notification('success','Scenario deleted!',request.session)
    # redirect to the general scenarios view
    return redirect('scenarios')

########################################################################################################################
def togglePublicScenario(request, scenario_id):
    upload = scenario.objects.get(id=scenario_id)
    upload.is_public = not upload.is_public
    upload.save()
    return HttpResponse(content=json.dumps({'is_public':upload.is_public}), content_type='application/json', status=200)

########################################################################################################################
@csrf_exempt
def updateScenarioContents(request):
    """
    Handles changing the contents of a scenario upload object (just the xml). This should be called only via AJAX
    """
    if not request.is_ajax or not request.method == "POST" or request.POST["scenario_id"] is None or request.POST["scenario_contents"] is None:
        # If the request is not an ajax call, or does not contain both scenario_id and scenario_contents parameters then return an error
        return HttpResponse(status=400)
    # Get the relevant scenario upload object
    upload = scenario.objects.get(id=request.POST.get('scenario_id'))
    # Set the contents to the new value
    upload.contents = request.POST.get('scenario_contents')
    # Change the modified date
    upload.modified_on = datetime.now(tz=timezone.get_default_timezone())

    #validate xml schema from OpenMalaria
    output = ''+validateScenarioUploadContents(upload.contents)
    if len(output) > 0:
        #if there was any error, the length will be greater than 0... put the error in a notification and render self.
        return HttpResponse(content=json.dumps({'success':False ,'message':output}), content_type='application/json', status=200)

    # Save
    upload.save()

    # return the modification date so that the user interface can be updated (via javascript on the page)
    return HttpResponse(content=json.dumps({'success':True ,'modified':upload.modified_on.strftime('%Y-%m-%d %H:%M:%S')}), content_type='application/json', status=200)


########################################################################################################################
class ScenarioParamsView(TemplateView):
    template_name="scenarioParams.html"

########################################################################################################################
@csrf_exempt
def defineScenarioParams(request):
    """
    Handles the continuation of the scenario upload process if variables were found in the XML. This should be called only via AJAX
    """
    if request.is_ajax() and request.method == "POST":
        # If the request is ajax and using POST method, load the json object
        upload_contents = json.loads(request.body)
        # if upload_contents is not empty...
        if upload_contents is not None:
            #Create the new upload object
            upload = scenario()
            # Set the name
            upload.name = upload_contents['scenario_name']
            # Set the description
            upload.description = upload_contents['scenario_description']
            # Set the scenario contents
            upload.contents = upload_contents['scenario_contents']
            # Set public is necessary
            if upload_contents['scenario_public'] == 'True':
                upload.is_public = upload_contents['scenario_public']
            # Define the upload provenance
            upload.created_on = datetime.now(tz=timezone.get_default_timezone())
            upload.modified_on = upload.created_on
            upload.created_by = request.user
            # Save it to the database
            upload.save()
            # Handle the user defined parameters
            parameters = upload_contents['parameters']
            for param in parameters:
                new_param = scenarioParameter()
                new_param.param_id = param['param_id']
                new_param.description = param['description']
                new_param.default_value = param['default_value']
                new_param.scenario = upload
                new_param.save()
            set_notification('success','New scenario configuration successfully created!',request.session)
            return HttpResponse(status=200)
        else:
            return HttpResponse(status=400)
    return HttpResponse(status=400)


def validateScenarioUploadContents(contents):
    #This method runs the OpenMalaria simulation with the validate-only flag. Returns an empty string if everything is valid. Otherwise returns the error
    openmalaria_data_dir = "/omdata"
    om_exe = "/omdata/build/openMalaria"
    simulation_dir = os.path.join(openmalaria_data_dir,'validation')
    filename = '%d.xml' % int(round(time.time()))
    file = open(os.path.join(simulation_dir,filename),'w')

    #IMPORTANT! Need to replace all parameter variables (ie. "@paramname@") with dummy values for validation purposes. It will fail with '@'.
    tmpContents = re.sub(r'@(.*?)@', '0', contents)

    file.write(tmpContents)
    file.close()
    output = ''
    omprocess = subprocess.Popen([om_exe,"--scenario",filename, '--validate-only'], shell=False,cwd=simulation_dir,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while True:
        out = omprocess.stderr.readline()
        if out == '' and omprocess.poll() is not None:
            break
        if out != '':
            output += out
    os.remove(os.path.join(simulation_dir,filename))
    return output


