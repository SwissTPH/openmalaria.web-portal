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
    $('#navmenu_experiments').addClass('selected_menu');

    ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//OLD FUNCTIONALITY BEGINS HERE
    $('#new_experiment_description_textarea').keyup(function () {
        var left = 1000 - $(this).val().length;
        if (left < 0) {
            left = 0;
        }
        $('#counter').text('Characters remaining: ' + left);
    });

    $('#new_experiment_submit').click( function () {
        $('#should_execute_experiment').val(1);
        $('#experiment_submission_form').submit();
    });

    $('#save_experiment_submit').click( function () {
        $('#should_execute_experiment').val(0);
        $('#experiment_submission_form').submit();
    });

    $('#experiment_submission_form').submit(function (){
        var valid = true;
        var descriptionText = $('#new_experiment_description_textarea').val();
        var titleText = $('#new_experiment_name').val();
        var scenarioFile = $('#current_scenario').val();

        var params = createParametersObject();
        if (params === null) {
            valid = false;
        } else {
            $('#parameters').val(params);
        }

        //TODO validate experiment variable input values.

        $('[id^="new_experiment_"]').removeClass('error_input');
        $('#submission_error').hide();

        if (titleText === undefined || titleText === null || titleText.length < 1){
            $('#new_experiment_name').addClass('error_input');

            valid = false;
        }

        if (descriptionText === undefined || descriptionText === null || descriptionText.length < 1){
            $('#new_experiment_description_textarea').addClass('error_input');
            valid = false;
        }

        if (!valid) {
            $('#submission_error').html('Marked fields are required!').show();
        } else {
            $('#new_experiment_description').val(descriptionText); //set the hidden field value so it appears in POST[]
        }
        return valid;

    });


    $('input[id^="input_"]').keyup(function (){
        var simCount = estimateSimCount();
        var maxSimCount = $('#sim_count_limit').val();
        if (maxSimCount == "0") maxSimCount = 1024;
        var disabledSave = simCount > maxSimCount;
        $('#expected_sim_count').text('Number of simulations expected: '+ simCount);

        $('#new_experiment_submit').prop('disabled',disabledSave);
        $('#save_experiment_submit').prop('disabled',disabledSave);

        if (disabledSave){
//                                $("#new_experiment_submit").attr("disabled", "disabled");
//                                $("#save_experiment_submit").attr("disabled", "disabled");
            $('#submission_error').html('This configuration exceeds your maximum allowed number of simulations.').show();

        } else {
//                                $("#new_experiment_submit").removeAttr("disabled");
//                                $("#save_experiment_submit").removeAttr("disabled");
            $('#submission_error').hide();
        }

    }); // following removed because need to allow text input
        // .keypress(function(event){
        //    var filter = /[-0-9:,.\r\n\b\t]/;
        //    return maskKeyPress(event, filter)
        //});

    simCount = estimateSimCount();
    $('#expected_sim_count').text('Number of simulations expected: '+ simCount);

});

function estimateSimCount() {
    var simCount = 1;
    $('input[id^="input_"]').each(function (){
        var value = $(this).val();
        if (value.split(':').length != 3){
            if (value.split(',').length < 2){
                simCount *= 1;
            } else {
                // parse out sequence
                simCount *= value.split(',').length;
            }
        } else {
            // parse out range
            var paramSims = 0;
            var rangeParts = value.split(':');
            if (rangeParts[0].length > 0 && rangeParts[1].length > 0 && rangeParts[2].length > 0) {
                var min = rangeParts[0];
                var max = rangeParts[1];
                var step = rangeParts[2];
                paramSims = Math.floor((max-min)/step);
                simCount *= paramSims;
            }
        }
    });
    return simCount;
}

function createParametersObject() {
    var nullValueOccurred = false;
    var parameters = [];
    var jObject = {};
    jObject.parameters = parameters;

    $('input[id^="input_"]').each(function (){

        if ($(this) !== undefined && $(this) !== null && $(this).val() !== null) {
            var object = {};
            var id = $(this).attr('id').substr(6); //The id subtracting 'input_'
            var value = $(this).val();

//            object["param_id"] = id;
            object["id"] = id;
            object["value"] = value;
            parameters.push(object);
        } else {
            alert("Undefined value occurred");
        }
    });

    if (nullValueOccurred){
        alert('All values are required. Please enter something in each field and try again.');
        return null;
    }
    console.log(JSON.stringify(jObject));
    return JSON.stringify(jObject);
}
