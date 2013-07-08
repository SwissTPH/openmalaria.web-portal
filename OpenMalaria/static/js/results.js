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

function getExperimentContent(){
    //get the current experiment selection (experiment id)
    var selection_id = $('#available_experiments').val();
    //if the id != 0 (the user already exists)
    if (selection_id > 0 ){
        // Show the loading
        $('#waiting').show();
        // hide the information table
        $('#experiment_view_table').hide();
        //set the hidden id field of current selection
        $('#experiment_id').val(selection_id);
        //start an ajax request to get selection info by passing in the relevant info
        $.ajax({type: 'GET', url: '/results/', data: {'experiment_id': selection_id },
            //on success, populate the table values
            success: function(response) {
                $('#experiment_name').text(response.experiment_name);
                $('#experiment_description').text(response.experiment_description);
                $('#experiment_start').text(response.experiment_started);
                $('#experiment_sim_count').text(response.experiment_sim_count);
                $('#experiment_boinc').text(response.boinc);
                appendSimData(response.experiment_sims, response.boinc !='No');
                $('input[id^="button_"]').removeAttr('disabled');

            },
            //on error show an alert.
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
    } else {
        //if the user id !> 0 (unknown experiment), prevent attempts to delete/download unknown experiments
        $('input[id^="button_"]').attr('disabled', 'disabled');
    }
}

$(document).ready(function() {
    // Call the content a first time in case something is selected
    getExperimentContent();

    $('#navmenu_results').addClass('selected_menu');

    //Disable the buttons because there is currently no selection
    $('input[id^="button_"]').attr('disabled', 'disabled');


    $('#available_experiments').change( function(){
        getExperimentContent();
    });

    //Why was this moved out of the document.ready function?
    $('#button_duplicate_experiment').attr('disabled','disabled').click(function(){
        var current_exp = $('#available_experiments').val();
        window.location= '/duplicateExperiment/'+ current_exp;
    });


    $('#button_delete_experiment').click( function(){
        $('#delete_dialog').dialog('open');
    });

    //handle the delete dialog choice.
    $('#delete_dialog').dialog({autoOpen:false, modal: true, resizable: false,
        buttons: {
            //If delete operation canceled, close the dialog
            'Cancel': function() { $(this).dialog('close'); },
            //If delete should occur, issue the command
            'Ok': function() { window.location.href = '/deleteSimulationGroup/'+$('#experiment_id').val()}
        }
    });

    $('#view_dialog').dialog({autoOpen:false, modal: true, resizable: false, width: 'auto',
        buttons: {'Ok': function() { $(this).dialog('close'); }}
    });

    $('#button_download_experiment').click( function(){
        var path = '/downloadExperimentResults/'+ $('#experiment_id').val();
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

    $('#view_base_scenario').click( function(){
        var exp_id = $('#experiment_id').val();
        $.ajax({type: 'GET', url: '/downloadExperimentBaseXML/'+exp_id,
            //on success, populate the table values
            success: function(response) {
                $('#view_contents').text(response).scrollTop(0);
                prettyPrint();

                $('#view_dialog').dialog('option', 'title', 'XML Scenario for Simulation #'+exp_id).dialog('open');
            },
            //on error show an alert.
            error: function() {
                $('#exception_dialog').dialog('open');
            }
        });
    });

});

function appendSimData(sims, boinc){
    $('#experiment_view_table').find('tr[id^="sim_info_"]').remove();

    $.each(sims, function (key,val){
        var rowHTML = '<tr id=\"sim_info_'+key+'\">';
        var simStatus;
        if (val.sim_status === 100){
            simStatus = 'Complete';
        } else if (val.sim_status < 0 && val.sim_message !== null){
            simStatus = val.sim_message;
        } else {
            simStatus = 'Unknown'
        }

        rowHTML += '<td>Sim #'+key+'</td>';
        if (val.sim_status === 100){
            rowHTML += '<td class=\"help_text\">('+simStatus+') ';
            // Only ctsout for the non BOINC
            if (!boinc) {
                rowHTML += '<input type=\"button\" value=\"View Ctsout\" id=\"sim_ctsout_'+key+'\" style=\"float:right;\"/>';
            }
            rowHTML += '<input type=\"button\" value=\"View Results\" id=\"sim_res_'+key+'\" style=\"float:right;\"/>';
        } else {
            rowHTML += '<td class=\"error_text\">('+simStatus+') ';
            rowHTML += '<input type=\"button\" value=\"Relaunch Simulation\" id=\"sim_lau_'+key+'\" style=\"float:right;\"/>';
        }
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

    if (!boinc) {
        // add the display dialog functionality to ctsout buttons
        $('input[id^="sim_ctsout_"]').click( function(){
            var sim_id = $(this).attr('id').substring(11);
            $.ajax({type: 'GET', url: '/downloadCtsout/'+sim_id,
                //on success, populate the table values
                success: function(response) {
                    $('#view_contents').text(response);
                    prettyPrint();
                    $('#view_dialog').dialog('option', 'title', 'Ctsout File for Simulation #'+sim_id).dialog('open');
                },
                //on error show an alert.
                error: function() {
                    $('#exception_dialog').dialog('open');
                }
            });

        });
    }

    // add the display dialog functionality to Results buttons
    $('input[id^="sim_res_"]').click( function(){
        var sim_id = $(this).attr('id').substring(8);
        $.ajax({type: 'GET', url: '/downloadResults/'+sim_id,
            //on success, populate the table values
            success: function(response) {
                $('#view_contents').text(response);
                prettyPrint();
                $('#view_dialog').dialog('option', 'title', 'Results File for Simulation #'+sim_id).dialog('open');
            },
            //on error show an alert.
            error: function() {
                $('#exception_dialog').dialog('open');
            }
        });

    });

    // add the relaunch functionality to failed simulations
    $('input[id^="sim_lau_"]').click( function(){
        //alert('This functionality is not implemented yet!')
        var sim_id = $(this).attr('id').substring(8);
        $.ajax({type: 'GET', url: '/relaunchSimulation/'+sim_id,
            //on success, populate the table values
            success: function(response) {
                if (response.result){
                    window.location = '/results';
                } else {
                    $('#exception_dialog').dialog('open');
                }
            },
            //on error show an alert.
            error: function() {
                $('#exception_dialog').dialog('open');
            }
        });
    });


}