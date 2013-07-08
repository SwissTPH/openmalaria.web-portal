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
    var maxTextareaLength = 1000;
    $('#counter').text('Characters remaining: ' + maxTextareaLength);
    $('#navmenu_scenarios').addClass('selected_menu');

    // This function, tied to the "new_scenario_description" text area, enforces the 1000 character limit.
    // It updates the "Characters remaining" label to provide feedback
    $('#new_scenario_description_textarea').keyup(function () {
        var stringVal = $(this).val();
        var left = maxTextareaLength - stringVal.length;
        if (left <= 0) {
            left = 0;
            $(this).val(stringVal.substr(0,maxTextareaLength));
        }
        $('#counter').text('Characters remaining: ' + left);
    });


    // This function validates the scenario submission form and submits if all data is valid.
    // Otherwise, it highlights information that is required
    $('#scenario_submission_form').submit(function (){
        var valid = true;
        var descriptionText = $('#new_scenario_description_textarea').val();
        var titleText = $('#new_scenario_name').val();
        var uploadFile = $('#new_scenario_file').val();

        $('[id^="new_scenario_"]').removeClass('error_input');
        $('#submission_error').hide();

        if (titleText === undefined || titleText === null || titleText.length < 1){
            $('#new_scenario_name').addClass('error_input');
            valid = false;
        }

        if (descriptionText === undefined || descriptionText === null ||  descriptionText.length < 1){
            $('#new_scenario_description_textarea').addClass('error_input');
            valid = false;
        }

        if (uploadFile === undefined || uploadFile === null  ||  uploadFile.length < 1){
            $('#new_scenario_file').addClass('error_input');
            valid = false;
        }

        if (!valid) {
            $('#submission_error').show();
        } else {
            $('#submission_error').hide();
            $('#new_scenario_description').val(descriptionText); //set the hidden field value so it appears in POST[]
        }
        return valid;

    });

});
