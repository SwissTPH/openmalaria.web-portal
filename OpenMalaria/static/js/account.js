/*
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
*/

$(document).ready(function() {
 */
    $('#navmenu_account').addClass('selected_menu'); //make the "Account Management" tab "active"
    //disable the delete button until a selection is made and open the dialog when it's clicked
    $('#delete_user').attr('disabled', 'disabled').click( function(){
        $('#delete_dialog').dialog('open');
    });

    //handle clicks when the selected user changes
    $('#available_users').change( function (){

        //get the current user id
        var current_user_id = $('#current_user_id').val();
        //get the current user selection (user id)
        var selection_id = $('#available_users').val();
        //if the id != 0 (the user already exists)
        // remove error coloring for fields
        $('[id^="user_"]').removeClass('error_input');
        // hide previously generated errors
        $('#user_save_error').html('');
        // clear out any password values
        $('[id^="user_password_"]').val('');
        if (selection_id > 0 ){
            // Show the loading
            $('#waiting').show();
            // hide the information table
            $('#user_edit_table').hide();
            //set the hidden id field of current selection
            $('#user_id').val(selection_id);
            //prevent the user from changing their own permissions/limitations!
            $('.extra_admin').toggle(current_user_id !== selection_id);
            //start an ajax request to get selection info by passing in the relevant info
            $.ajax({type: 'GET', url: '/account/', data: {'user_id': selection_id },
                //on success, populate the table values
                success: function(response) {
                    $('#user_username').val(response.user_username);
                    $('#user_first_name').val(response.user_first_name);
                    $('#user_last_name').val(response.user_last_name);
                    $('#user_email').val(response.user_email);
                    $('#user_max_sims').val(response.user_max_sims);
                    $('#user_is_active').prop('checked', response.user_is_active);
                    $('#user_is_staff').prop('checked', response.user_is_staff);
                    $('#user_use_boinc').prop('checked', response.user_use_boinc);
                    $('#user_post_public').prop('checked', response.user_post_public);
                    $('#delete_user').prop('disabled',(selection_id === current_user_id ));
                },
                //on error show an alert.
                error: function() {
                    $('#exception_dialog').dialog('open');
                },
                complete: function(){
                    // hide the loading
                    $('#waiting').hide();
                    // display the information table
                    $('#user_edit_table').show();
                }
            });
        //if the user id !> 0 (unknown user), prevent attempts to delete unknown users
        } else {
            //simply disable the delete button
            $('#delete_user').attr('disabled', 'disabled');
        }
        // toggle the display of the information table (ignore next line in favor of ajax version)
        //$('#user_edit_table').toggle(selection_id > 0);
    });

    //handle click request to create a new user
    $('#create_user').click( function(){
        // Clear the user selection
        $('#available_users').val([]);
        // disable delete functionality
        $('#delete_user').attr('disabled', 'disabled');
        // reset all text fields
        $('input[id^="user_"]').val("");
        // clear the hidden id field
        $('#user_id').val('');
        // is_active on by default
        $('#user_is_active').attr('checked', true);
        // is_staff off by default
        $('#user_is_staff').attr('checked', false);
        // use_boinc off by default
        $('#user_use_boinc').attr('checked', false);
        // post_public off by default
        $('#user_post_public').attr('checked', false);
        // max_sims = 0 by default
        $('#user_max_sims').val(0);
        // hide previously generated errors
        $('#user_save_error').text('');
        // remove error coloring for fields
        $('[id^="user_"]').removeClass('error_input');
        // show the "extra" admin options
        $('.extra_admin').show();
        // show the edit table
        $('#user_edit_table').show();
    });

    //handle the delete dialog choice.
    $('#delete_dialog').dialog({autoOpen:false, modal: true, resizable: false,
        buttons: {
            //If delete operation canceled, close the dialog
            'Cancel': function() { $(this).dialog('close'); },
            //If delete should occur, issue the command
            'Ok': function() { window.location.href = '/deleteUser/'+$('#user_id').val()}
        }
    });

    //handle unknown exceptions
    $('#exception_dialog').dialog({autoOpen:false, modal: true, resizable: false, buttons: { "Ok": function() { $(this).dialog("close"); }}});

    //handle when the user presses the "Save Changes" box
    $('#save_user_button').click( function(){
        //Remove error_input class from all fields
        $('[id^="user_"]').removeClass('error_input');
        //Clear out the error message
        $('#user_save_error').text('');
        //Create a javascript object representing the current state of the form
        var alteredUser = createUserObject();
        //Perform a rudimentary error check pre-submission
        var error = alteredUser.checkForErrors();
        //If there was an error, update the interface to show it
        if (error !== null){
            updateInterfaceForError(error);
        } else {
            //If no error then save via ajax
            $.ajax({
                type: 'POST',
                url: '/saveUser/',
                data: {'user_object': JSON.stringify(alteredUser) },
                success: function(response) {
                    if (response.success){
                        window.location.href = '/account/'; // Refresh to show success notification
                    } else {
                        var error = response.error;
                        updateInterfaceForError(error);
                    }
                },
                error: function() {
                    $('#exception_dialog').dialog('open');
                }
            });
        }

    });

    $('#user_max_sims').keypress(function (event){
        var filter = /[0-9\r\n\b\t]/;
        return maskKeyPress(event, filter)

    });

    initializeSelection();

});


function initializeSelection(){
    //Set the initial user selection to the current user's account
    $('#available_users').val($('#current_user_id').val()).change();
}


function updateInterfaceForError(error){
    if (error !== undefined || error !== null || error.length !== 0){
        $('#user_save_error').text(error);
        if (error.indexOf('First') !== -1){
            $('#user_first_name').addClass('error_input');
        }
        if (error.indexOf('Last') !== -1){
            $('#user_last_name').addClass('error_input');
        }
        if (error.indexOf('Username') !== -1){
            $('#user_username').addClass('error_input');
        }
        if (error.indexOf('email') !== -1){
            $('#user_email').addClass('error_input');
        }
        if (error.indexOf('Passwords') !== -1){
            $('#user_password').addClass('error_input');
            $('#user_password_conf').addClass('error_input');
        }
    }
}

// Convenience function to grab all information about currently selected user and return a js dictionary
function createUserObject(){
    var user = {};
    user.user_id = $('#user_id').val();
    user.user_first_name = $('#user_first_name').val();
    user.user_last_name = $('#user_last_name').val();
    user.user_username = $('#user_username').val();
    user.user_email = $('#user_email').val();
    user.user_max_sims = $('#user_max_sims').val();
    user.user_password = $('#user_password').val();
    user.user_password_conf = $('#user_password_conf').val();
    user.user_is_active = $('#user_is_active').attr('checked');
    user.user_is_staff = $('#user_is_staff').attr('checked');
    user.user_use_boinc = $('#user_use_boinc').attr('checked');
    user.user_post_public = $('#user_post_public').attr('checked');
    user.checkForErrors = function (){
        if (this.user_id === null ||this.user_id.length === 0){
            this.user_id = 0;
        }
        if (this.user_max_sims === null || this.user_max_sims.length === 0){
            this.user_max_sims = 0;
        }
        if (this.user_first_name.length === 0){
            return 'First name is required.';
        }
        if (this.user_last_name.length === 0){
            return 'Last name is required.';
        }
        if (!this.isEmailValid()){
            return 'Valid email address is required.';
        }
        if (this.user_username.length === 0){
            return 'Username is required.';
        }
        if (this.user_password !== this.user_password_conf){
            return 'Passwords do not match.';
        }
        return null;
    };
    user.isEmailValid = function (){
        //this regular expression was grabbed from the web (http://stackoverflow.com/questions/2855865/jquery-validate-e-mail-address-regex)
        var re = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
        return re.test(this.user_email);
    };

    return user;
}
