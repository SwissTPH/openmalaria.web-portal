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
    $('#navmenu_experiments').addClass('selected_menu');
    prettyPrint();

    $('#button_download_experiment').attr('disabled','disabled').click( function(){
        var path = '/downloadExperimentResults/'+ $('#current_experiments').val();
        var $download_dialog = $('#download_dialog');
        $download_dialog.dialog({modal:true, resizable: false});
        $.fileDownload(path, {
            successCallback: function () {
                $download_dialog.dialog('close');
            },
            failCallback: function () {
                $download_dialog.dialog('close');
                $('#$download_error_dialog').dialog({ modal: true, resizable:false });
            }
        });
    });

    $('#button_delete_experiment').attr('disabled','disabled').click(function(){
        $('#delete_dialog').dialog('open');
    });

    $('#button_launch_experiment').attr('disabled','disabled');

    $('#button_duplicate_experiment').attr('disabled','disabled').click(function(){
        var current_exp = $('#current_experiments').val();
        window.location= '/duplicateExperiment/'+ current_exp;
    });

    $('#button_create_experiment').click( function(){
       window.location = '/createExperiment/'
    });

    $('#current_experiments').change( function () {

        var experiment_id = $('#current_experiments').val();
        var invalid_id = experiment_id <= 0;
        $('#experiment_parameters').find('tr').remove();
        $('#experiment_details').hide();

        $('#button_delete_experiment').prop('disabled',invalid_id);
        $('#button_download_experiment').prop('disabled',invalid_id);
        $('#button_launch_experiment').prop('disabled',invalid_id);
        $('#button_duplicate_experiment').prop('disabled',invalid_id);

        if (!invalid_id ){
            // Show the loading
            $('#waiting').show();
            // hide the information table
            $('#experiment_view_table').hide();
            $.ajax({
                type: 'GET',
                url: '/experiments/',
                data: {'current_experiment': experiment_id },
                success: function(response) {
                    $('#experiment_name').html(response.name);
                    $('#experiment_description').html(response.description);
                    $('#experiment_user').html(response.user);
                    $('#experiment_date').html(response.date);
                    $('#experiment_boinc').html(response.boinc);
                    $('#view_contents').text(response.content);
                    $('#experiment_sim_count').text(response.experiment_sim_count);
                    appendSimData(response.experiment_sims);

                    var param_count = 0;
                    var params_in_scenario = response.params_in_scenario;
                    $.each(response.parameters, function(key,val) {
                        $('#experiment_parameters').append('<tr><th>'+key+' (@'+params_in_scenario[key]+'@):</th><td>'+val.join(", ")+'</td></tr>');

                        param_count = param_count + 1;
                    });
                    if (param_count <= 0){
                        $('#experiment_parameters').append('<tr><th></th><td>No parameters defined (single run scenario).</td></tr>');
                    }


                },
                error: function() {
                    $('#exception_dialog').dialog('open');
                },
                complete: function(){
                    // hide the loading
                    $('#waiting').hide();
                    // display the information table
                    $('#experiment_view_table').show();
                }
            });
        }

        prettyPrint();
        $('#experiment_launch_id').val(experiment_id);
        //Disabled while in favor of ajax status-based updates
        //$('#experiment_view_table').toggle(experiment_id > 0);

    });

    /**
     * Handle click on "Delete experiment" button for an experiment.
     */
    $('#delete_dialog').dialog({autoOpen:false, modal: true, resizable: false,
        buttons: {
            //If delete operation canceled, close the dialog
            "Cancel": function() { $(this).dialog("close"); },
            //If delete should occur, issue the command
            "OK": function() { window.location.href = '/deleteExperimentGroup/'+$("#current_experiments").val()}
        }
    });

    $('#view_dialog').dialog({autoOpen:false, modal: true, resizable: false, width: 'auto',
        buttons: {"OK": function() { $(this).dialog("close"); }}
    });

    $('#view_base_scenario').click( function(){
        prettyPrint();
        $('#view_dialog').dialog('open');
    });

});

function appendSimData(sims){
    $('#experiment_view_table').find('tr[id^="sim_info_"]').remove();

    $.each(sims, function (key,val){
        var rowHTML = '<tr id=\"sim_info_'+key+'\">';
        var simStatus = 'Not launched';
        rowHTML += '<td>Sim #'+key+'</td>';
        rowHTML += '<td class=\"help_text\">('+simStatus+') ';
        rowHTML += '<input type=\"button\" value=\"View XML\" id=\"sim_xml_'+key+'\" style=\"float:right;\"/>';
        rowHTML += '</td></tr>';
        if ($.keys(val.parameters).length > 0){
            rowHTML += '<tr class=\"innerbox_table\" id=\"sim_info_'+key+'\"><td>Parameters:</td><td>';
            $.each(val.parameters, function (param_key,param_val){
                rowHTML += '<b>'+param_key+':</b> '+param_val+'<br />';
            });
            rowHTML += '</td></tr>';
        }
        $('#experiment_view_table').append(rowHTML);

    });

    // add the display dialog functionality to XML buttons
    $('input[id^="sim_xml_"]').click( function(){
        var sim_id = $(this).attr('id').substring(8);
        $.ajax({type: 'GET', url: '/downloadSimulationXML/'+sim_id,
            //on success, populate the table values
            success: function(response) {
                $('#view_contents').text(response);
                prettyPrint();
                $('#view_dialog').dialog('option', 'title', 'XML Scenario for Simulation #'+sim_id).dialog('open');
            },
            //on error show an alert.
            error: function() {
                $('#exception_dialog').dialog('open');
            }
        });

    });

}
