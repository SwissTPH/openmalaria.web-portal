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

from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum


class scenario(models.Model):
    """
    Scenario upload represents an XML file uploaded by a user
    """
    name = models.CharField(max_length=100,null=True)
    description = models.CharField(max_length=1000, null=True)
    # User who uploaded the scenario
    created_by = models.ForeignKey(User, related_name='scenario_created_by', null=True)
    # Date this scenario was created on
    created_on = models.DateTimeField(auto_now_add=True)
    # when the scenario was last modified
    modified_on = models.DateTimeField(auto_now_add=True)
    # the XML file to be used during the simulation run.
    contents = models.TextField()
    # Flag indicating whether or not this scenario is available to users other than the creator
    is_public = models.BooleanField(default=False)

class scenarioParameter(models.Model):
    """
    Represents the parameters @parameter_name@ in the scenarioUpload.
    The user gives a description and a default_value for each of these
    and this is the table where this information ends up.
    """
    # The @param_id@ value (excluding '@' symbols)
    param_id = models.CharField(max_length=100)
    # Description specified from the UI - human readable version of what the @param_name@ represents
    description = models.CharField(max_length=100)
    # Default value(s) that can replace the placeholder. Note this contains a single value, a comma-separated list of values
    # or a range indicated by start:stop:increment.
    default_value = models.CharField(max_length=100)
    # Owning scenario
    scenario = models.ForeignKey(scenario, related_name='parameters')

class experiment(models.Model):
    """
    Represent an experiment.
    An experiment has a base scenario
    And parameters (experimentParameters)
    """
    # Title of the group to be displayed in UI
    name = models.CharField(max_length=100)
    # Description specified from the UI
    description = models.CharField(max_length=1000)
    # the XML file to be used during the simulation run. This is an exact copy of a scenarioUpload.contents used to create the experiment (to allow decoupling)
    contents = models.TextField()
    # User who created the group of simulations
    created_by = models.ForeignKey(User, related_name='experiment_created_by')
    # Date this group was created on
    created_on = models.DateTimeField(auto_now_add=True)
    # Flag indicating whether this group has been sent off to be run (may not be run on remote server yet though)
    launched = models.BooleanField(default=False)
    # Flag indicating if the entire group of simulations have completed (or canceled/error)
    finished = models.BooleanField(default=False)
    # Flag if scenarios in this experiment should be run using BOINC system
    use_boinc = models.BooleanField(default=False)

    def getStatus(self):
        """
        Return the status of the experiment.
        """
        status = dict()
        # Calculate the percentage done
        # This is done by adding all the status of the non-failed simulations + all the failed simulations as if they were done
        # and dividing up by the number of total simulations
        total_simulations = self.simulations.count()
        try:
            total_status_without_error = self.simulations.exclude(status=-1).values('experiment_id').annotate(total=Sum('status'))[0]["total"]
        except Exception, e:
            #The only case where this would get called is if ALL simulations failed
            total_status_without_error = 0
        failed_simulations =  self.simulations.filter(status=-1).count()
        total_status_error =  failed_simulations * 100
        percentage = (total_status_error + total_status_without_error)/total_simulations

        # Store in the dictionnary
        status["percentage_done"] = percentage
        status["failed_simulations"] = failed_simulations
        status["completed_simulations"] = self.simulations.filter(status=100).count()
        status["total_simulations"] = total_simulations
        if percentage == 100:
            self.finished = True
            self.save()
        return status

class experimentParameter(models.Model):
    """
    Represents a parameter for an experiment (derived from scenarioParameter).
    for ex: infectiousness: 0 to 100 with 1 increment
    """
    # The @param_id@ value (excluding '@' symbols) from corresponding scenarioUploadParam
    param_id = models.CharField(max_length=100)
    # The range of possibilities that can replace the placeholder. Note this contains a single value, a comma-separated list of values
    # or a range indicated by start:stop:increment.
    param_value = models.CharField(max_length=100)
    # Description defined in corresponding scenarioUploadParam
    description = models.CharField(max_length=100)
    # Owning experiment
    experiment = models.ForeignKey(experiment, related_name='parameters')



class simulationRun(models.Model):
    """
    This represents a single simulation.
    An experiment is composed by one or more of these.
    Some fields are duplicates of scenarioUpload/experiment model field because it must be decoupled from these models.
    """
    # the XML file to be used during the simulation run. This is a copy of a scenarioUpload.contents file with the parameters inserted (if any)
    contents = models.TextField()
    # time the simulation was started
    start_time = models.DateTimeField(null=True)
    # User starting the simulation
    user = models.ForeignKey(User, related_name='run_started_by')
    # 0-100 representing percent complete (-1 if there was an error or canceled)
    status = models.IntegerField(blank=False, default=0)
    # Human readable text for error messages
    message = models.CharField(max_length=10000, null=True)
    # Experiment
    experiment = models.ForeignKey(experiment, related_name='simulations', null=True)
    # A unique id (uuid for cluster jobs; ndom_#_uuid for Boinc jobs where # is the id of this record)
    task_id = models.CharField(null=True, max_length=300)
    # Flag if ran/to be run using boinc
    use_boinc = models.BooleanField(default=False)
    # Flag indicating whether this simulation has been sent off to be run (may not be run on remote server yet though)
    launched = models.BooleanField(default=False)
    # Flag indicating that this simulation is complete (status may not be sufficient)
    finished= models.BooleanField(default=False)
    # Text field to hold the results from the simulation
    sim_results = models.TextField()
    # Text field to hold the additional output from the simulation
    sim_cts_out = models.TextField()

class simulationRunParameter(models.Model):
    """
    Identifies the parameters used in the simulationRun.
    Some fields are duplicates of scenarioUploadParam/experimentParameters because it must be decoupled from these models.
    """
    # The @param_id@ value (excluding '@' symbols) from corresponding scenarioUploadParam
    param_id = models.CharField(max_length=100)
    # Description defined in corresponding scenarioUploadParam
    description = models.CharField(max_length=100)
    # The value that actually replaces the placeholder for this particular simulationRun
    param_value = models.CharField(max_length=100)
    # Owning simulationRun object
    simulationRun = models.ForeignKey(simulationRun, related_name='parameters')

class additionalUserInfo(models.Model):
    """
    Other attributes associated with a give User.
    This serves the same functionality as the built in Django 1.4 user profile model, but that is deprecated as of 1.5 and
    a better option in the future would be to use a custom user model altogether. Because of the uncertainty around these
    changes, this approach was used (also because it allowed to get up and running rather quickly).
    """
    # Defines the maximum number of simulations per experiment that can be run (a value of 0 represents no limit)
    max_sims = models.IntegerField(default=0)
    # Determines whether the user can utilize the BOINC submission system
    use_boinc = models.BooleanField(default=False)
    # Determines whether the user can make scenarios they upload publicly available
    post_public = models.BooleanField(default=False)
    # User to whom this additional information is associated
    user = models.ForeignKey(User, related_name='additionalUserInfo')
