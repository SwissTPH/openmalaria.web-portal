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
    $('#save_button').click(function(){
        $('input[id^="param_desc_"]').removeClass('error_input');
        var params = createParametersObject();
        if (params === null) {

        } else {
            $.ajax({
                type: 'POST',
                url: '/defineScenarioParams/',
                contentType: 'application/json; charset=utf-8',
                data: params,
                success: function() {
                    window.location = "/scenarios/";
                },
                error: function() {
                    alert("Unable to save parameters");
                }
            });
        }

    });

    //Disabled because this needs to be reworked to allow strings as well...
    //$('input[id^="param_default_"]').keypress(function (event){
    //    var filter = /[-0-9:,.\r\n\b\t]/;
    //    return maskKeyPress(event, filter)
    //});

});


function createParametersObject() {
    var nullValueOccurred = false;
    var parameters = [];
    var jObject = {};
    jObject.parameters = parameters;
    jObject.scenario_name = $('#scenario_name').val();
    jObject.scenario_description = $('#scenario_description').val();
    jObject.scenario_contents = $('#scenario_contents').val();
    jObject.scenario_public = $('#scenario_public').val();

    // Test to make sure there is something in all fields (basic validation)
    $('input[id^="param_"]').each(function(){
        if (!$(this).val()){
            $(this).addClass('error_input');
            nullValueOccurred = true;
            $('#submission_error').show();
        }
    });

    // validate the input pattern to be either single, comma-separated or colon-delimited range

    $('input[id^="param_desc_"]').each(function (){

        var object = {};
        var id = $(this).attr('id').substr(11);
        var description = $(this).val();
        var defSelect = "param_default_"+id;
        var defaultInput = $('#'+defSelect).val();
        if (description == "" || defaultInput == ""){
            nullValueOccurred = true;
        }
        object["param_id"] = id;
        object["description"] = description;
        object["default_value"] = defaultInput;
        parameters.push(object);
    });

    if (nullValueOccurred){
        return null;
    }
    return JSON.stringify(jObject);
}

