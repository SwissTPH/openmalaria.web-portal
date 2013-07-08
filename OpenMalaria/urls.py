import os
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from OpenMalaria import settings
from frontend.views.experimentViews import ExperimentView, ExperimentCreateView, ExperimentDuplicateView
from frontend.views.generalViews import HomeView, DashboardView
from frontend.views.resultViews import ResultsView
from frontend.views.scenarioViews import ScenarioView, ScenarioParamsView, ScenarioCreateView
from frontend.views.accountViews import AccountView
from django.contrib.auth import urls



admin.autodiscover()

urlpatterns = patterns('',
    # Uncomment the admin/doc line below to enable admin documentation:
    #url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # Uncomment the next line to enable the admin:
    #url(r'^admin/', include(admin.site.urls)),

    # Login
    url(r'^$', HomeView.as_view(), name='login'),
    url(r'ajaxAuth/', 'frontend.views.generalViews.ajaxAuth', name='ajaxAuth'),
    url(r'logout/', 'frontend.views.generalViews.performLogout', name='performLogout'),
    url(r'password/', include('django.contrib.auth.urls')),

    # Dashboard
    url(r'dashboard/', login_required(DashboardView.as_view()), name='dashboard'),
    url(r'getUserSimulationStatus/', 'frontend.views.generalViews.getUserSimulationStatus', name='simulationStatus'),

    # Account
    url(r'account/', login_required(AccountView.as_view()), name='account'),
    url(r'deleteUser/(?P<user_id>\d+)', 'frontend.views.accountViews.delete_user', name="delete_user"),
    url(r'saveUser/', 'frontend.views.accountViews.save_user', name="save_user"),

    # Results
    url(r'results/', login_required(ResultsView.as_view()), name='results'),
    url(r'relaunchSimulation/(?P<sim_id>\d+)', 'frontend.views.resultViews.relaunch_simulation', name='relaunch_simulation'),

    # Scenarios View
    url(r'scenarios/', login_required(ScenarioView.as_view()), name='scenarios'),
    url(r'createScenario/', login_required(ScenarioCreateView.as_view()), name='scenarioCreate'),
    url(r'scenarioParams/', login_required(ScenarioParamsView.as_view()), name='scenarioParams'),
    url(r'updateScenarioContents/', 'frontend.views.scenarioViews.updateScenarioContents', name='updateScenarioContents'),
    url(r'deleteScenario/(?P<scenario_id>\d+)', 'frontend.views.scenarioViews.deleteScenario', name='deleteScenario'),
    url(r'defineScenarioParams/', 'frontend.views.scenarioViews.defineScenarioParams', name='defineScenarioParams'),
    url(r'togglePublicScenario/(?P<scenario_id>\d+)', 'frontend.views.scenarioViews.togglePublicScenario', name='togglePublicScenario'),

    # Experiment (Simulation Group) View
    url(r'experiments/', login_required(ExperimentView.as_view()), name='experiments'),
    url(r'createExperiment/', login_required(ExperimentCreateView.as_view()), name='experimentCreate'),
    url(r'deleteSimulationGroup/(?P<experiment_id>\d+)', 'frontend.views.experimentViews.deleteSimulationGroup', name='simulationGroupDelete'),
    url(r'deleteExperimentGroup/(?P<experiment_id>\d+)', 'frontend.views.experimentViews.deleteExperimentGroup', name='experimentGroupDelete'),
    url(r'downloadScenario/(?P<run_id>\d+)', 'frontend.views.experimentViews.downloadScenarioXML', name='downloadScenarioXML'),
    url(r'cancelRun/(?P<runid>\d+)', 'frontend.views.experimentViews.cancelRun', name='cancelRun'),
    url(r'duplicateExperiment/(?P<experiment_id>\d+)', login_required(ExperimentDuplicateView.as_view()), name='experimentDuplicate'),
    url(r'duplicateExperiment/', login_required(ExperimentDuplicateView.as_view()), name='experimentDuplicatePost'),


    # Ajax methods
    #url(r'launchScenario/', 'frontend.views.scenarioViews.launchScenario', name='launchScenario'),
    url(r'downloadResults/(?P<simulationId>\d+)', 'frontend.views.generalViews.downloadResults', name='downloadResults'),
    url(r'downloadCtsout/(?P<simulationId>\d+)', 'frontend.views.generalViews.downloadCtsout', name='downlaodCtsout'),
    url(r'downloadSimulationXML/(?P<simulationId>\d+)', 'frontend.views.generalViews.downloadSimulationXML', name='downloadSimulationXML'),
    url(r'downloadExperimentBaseXML/(?P<experimentId>\d+)', 'frontend.views.generalViews.downloadExperimentBaseXML', name='downloadExperimentBaseXML'),
    url(r'downloadExperimentResults/(?P<experimentId>\d+)', 'frontend.views.generalViews.downloadExperimentResults', name='downloadExperimentResults'),
    url(r'defineExperiment/', 'frontend.views.experimentViews.defineExperiment', name='defineExperiment'),
    url(r'launchExperiment/', 'frontend.views.experimentViews.launchExperiment', name='launchExperiment'),

    url(r'pollBoincJobs/', 'frontend.views.generalViews.pollBoincJobs', name='pollBoincJobs'),

)

urlpatterns +=  patterns('',
    url(r'static/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': os.path.join(settings.PROJECT_PATH, 'static'),
        }),
    url(r'media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': os.path.join(settings.PROJECT_PATH, 'media'),
        }),
)
