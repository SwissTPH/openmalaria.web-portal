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

from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import TemplateView
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User, Group
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from frontend.models import additionalUserInfo
from frontend.views.generalViews import set_notification
import json

class AccountView(TemplateView):
    """
    AccountView - where user accounts can be modified (once logged in)
    """
    #Template file this view requires
    template_name = 'account.html'


    def get_context_data(self, **kwargs):
        """
        Method populates the context with data needed for the template file to be rendered.
        """
        #Get the default context from the superclass.
        context = super(AccountView, self).get_context_data(**kwargs)
        #Get the user objects that will appear in the list of modifiable users for the currently logged in user.
        context['available_users'] = get_modifiable_user_list(self.request.user)
        #Return the context
        return context

    def get(self, request, *args, **kwargs):
        """
        Handles HTTP GET requests. If request occurs via a URL, this method simply renders the AccountView template.
        If request occurs via AJAX, then it returns a json object representing the currently requested user. Note AJAX
        method requires a parameter named 'user_id' to be in the request or it will raise and exception and return code 400

        @param request: The http request object
        @param args: arguments
        @param kwargs: what else
        @return: Varies depending on the method used to access. Ajax returns a json object representing the user specified by
        'user_id' get parameter. Otherwise returns the view
        """
        if request.is_ajax():
            #If the request is AJAX, then...
            try:
                #Retrieve the user object with an id = 'user_id' get parameter.
                user = User.objects.get(id=request.GET['user_id'])
                #Retrieve the associated additionalUserInfo object.
                user_info = additionalUserInfo.objects.get(user_id = user.id)
                #Populate a JSON object containing the basic fields
                json_user_data = {
                    'user_username':user.username,
                    'user_email':user.email,
                    'user_is_active': user.is_active,
                    'user_first_name': user.first_name,
                    'user_last_name': user.last_name,
                    'user_max_sims': user_info.max_sims,
                    'user_use_boinc': user_info.use_boinc,
                    'user_post_public': user_info.post_public
                }
                #If the user making the request is a super user,
                if request.user.is_superuser:
                    #then define the 'user_is_staff' variable
                    json_user_data['user_is_staff']=user.is_staff
                #Finally return the JSON object
                return HttpResponse(content=json.dumps(json_user_data), content_type='application/json', status=200)

            except Exception as detail:
                #If an exception occurs, print the error to the log and return error code 400
                print detail
                return HttpResponse(status=400)
        else:
            #If the request is NOT AJAX, then simply render the template
            return self.render_to_response(self.get_context_data(**kwargs))

def get_modifiable_user_list(current_user):
    """
    Method to get a list of user objects that the currently logged in user can modify.
    @param current_user: The user object for the user making the request
    @return: a list of user objects that the requesting user has permission to modify (varies by privileges)
    """
    if current_user.is_superuser:
        #If superuser, then get all
        return User.objects.all().order_by('last_name')
    elif current_user.is_staff:
        #If current user is staff (an administrator capable of creating other accounts) allow them to modify themselves and all non-staff users
        return User.objects.filter(Q(id = current_user.id)|Q(is_staff = False)).order_by('last_name')
    else:
        #If user is not superuser or staff, they can only edit their own information.
        return User.objects.filter(id=current_user.id)


def delete_user(request, user_id):
    """
    Method to delete a user
    @param request: the HTTP request object
    @param user_id: the id of the user to be deleted
    @return:
    """
    try:
        #get the user with the parameter 'user_id'
        user_to_delete = User.objects.get(pk = user_id)
        #if the current user (one making request) has delete permissions
        if request.user.has_perm('auth.delete_user'):
            #delete the user
            user_to_delete.delete()
            #set a visual notification
            set_notification('success','User was successfully deleted.',request.session)
        else:
            #If the current user does NOT have delete permissions, notify them
            set_notification('error','You do not have permission to delete users.',request.session)
    except Exception as detail:
        #If an exception occurs, print it out to the log
        print detail
        #and notify the user
        set_notification('error','An unknown error occurred. User was not deleted',request.session)
    #Redirect to the accountView so notifications are visible.
    return HttpResponseRedirect('/account')

@csrf_exempt
def save_user(request):
    """
    Method to save either new or existing user information. Must be called via AJAX POST request. The request must contain
    a JSON object describing the user (in a 'user_object' request parameter).
    @param request: the HTTP request
    @return: A ja
    """
    if request.method == 'POST' and request.is_ajax():
        #If the request is an AJAX POST
        try:
            #A flag to determine if the user is new or already exists. Exists by default
            is_new = False
            #Load the JSON user object
            user_object = json.loads(request.POST.get('user_object'))
            #If the user_id is specified, try and load an existing user object
            if 'user_id' in user_object:
                #get the id of the user object
                user_id = user_object['user_id']
                try:
                    #get the user object corresponding to the 'user_id'
                    user = User.objects.get(pk = user_id)
                    #get the additional user info for the user
                    user_info = additionalUserInfo.objects.get(user_id=user_id)
                except Exception as detail:
                    #If an exception occurs, it will likely result because there is no user object with 'user_id' (a new user must be made)
                    print detail
                    #Create the new user object and additional user info object
                    user = User()
                    user_info = additionalUserInfo()
                    #mark the flag as a new user
                    is_new = True
                    # no existing user, assume we're creating a new one
            else:
                #if there is no user_id specified, then we must create a new user
                user = User()
                user_info = additionalUserInfo()
                is_new = True

            if 'user_username' in user_object:
                #make sure no one else has this username!
                if is_new:
                    if len(User.objects.filter(username=user_object['user_username'])) > 0:
                        return HttpResponse(content=json.dumps({'success': False, 'error': 'Username already in use.'}), content_type="application/json", status=200)
                else:
                    if len( User.objects.filter(username = user_object['user_username']).exclude(id=user.id) ) > 0:
                        return HttpResponse(content=json.dumps({'success': False, 'error': 'Username already in use.'}), content_type="application/json", status=200)
                user.username = user_object['user_username']
                if len(user.username) < 1:
                    return HttpResponse(content=json.dumps({'success': False, 'error': 'Username is required.'}), content_type="application/json", status=200)
            else:
                return HttpResponse(content=json.dumps({'success': False, 'error': 'Username is required.'}), content_type="application/json", status=200)

            if 'user_first_name' in user_object:
                user.first_name = user_object['user_first_name']
                if len(user.first_name) < 1:
                    return HttpResponse(content=json.dumps({'success': False, 'error': 'First name is required.'}), content_type="application/json", status=200)
            else:
                return HttpResponse(content=json.dumps({'success': False, 'error': 'First name is required.'}), content_type="application/json", status=200)

            if 'user_last_name' in user_object:
                user.last_name = user_object['user_last_name']
                if len(user.last_name) < 1:
                    return HttpResponse(content=json.dumps({'success': False, 'error': 'Last name is required.'}), content_type="application/json", status=200)
            else:
                return HttpResponse(content=json.dumps({'success': False, 'error': 'Last name is required.'}), content_type="application/json", status=200)

            if 'user_email' in user_object:
                user.email = user_object['user_email']
                if len(user.email) < 1:
                    return HttpResponse(content=json.dumps({'success': False, 'error': 'Valid email address is required.'}), content_type="application/json", status=200)
            else:
                return HttpResponse(content=json.dumps({'success': False, 'error': 'Valid email address is required.'}), content_type="application/json", status=200)

            if 'user_password' in user_object:
                if len(user_object['user_password']) > 0:
                    user.password = make_password(user_object['user_password'])

            if 'user_max_sims' in user_object:
                user_info.max_sims = user_object['user_max_sims']

            #These are simple boolean flags because the interface uses checkboxes to determine these user properties.
            user.is_active = 'user_is_active' in user_object
            user.is_staff = 'user_is_staff' in user_object
            user_info.use_boinc = 'user_use_boinc' in user_object
            user_info.post_public = 'user_post_public' in user_object

            #Save changes up to this point
            user.save()

            #Assign the 'account_creator' group (denoting Administrator, but not superuser, rights)
            group = Group.objects.get(name='account_creator')
            if user.is_staff:
                group.user_set.add(user)
            else:
                group.user_set.remove(user)
            #Assign user to the additional user info obejct and save it
            user_info.user = user
            user_info.save()
            #Make a notification to display to the user
            set_notification('success','Account information for <b>%s</b> was successfully saved!'% user.username,request.session)
            #Return a json object with 'success' property set to true
            return HttpResponse(content=json.dumps({'success': True}), content_type="application/json", status=200)
        except Exception as detail:
            print detail
    #If anything goes weird, then redirect to the accountView page.
    return HttpResponseRedirect('/account')
