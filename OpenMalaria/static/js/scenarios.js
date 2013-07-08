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
    $('#navmenu_scenarios').addClass('selected_menu');

    $('#button_upload_scenario').click( function(){
        window.location = '/createScenario/'
    });



    //This function monitors selection changes in the list of scenarios and pull (via Ajax) data about the scenario.
    // If the scenario is not a base scenario (ie. requires parameters to be specified) it can be launched directly.
    $('#current_scenarios').change( function () {

        var scenario_id = $("#current_scenarios").val();
        $("#scenario_parameters tr").remove();

        var invalid_id = scenario_id <= 0;
        $('#button_edit_scenario').prop('disabled',invalid_id);
        $('#button_delete_scenario').prop('disabled',invalid_id);

        if (!invalid_id ){
            // Show the loading
            $('#waiting').show();
            // hide the information table
            $('#scenario_view_table').hide();

            $.ajax({
                type: 'GET',
                url: '/scenarios/',
                data: {'current_scenario': scenario_id },
                success: function(response) {
                    $('#scenario_name').html(response.name);
                    $('#scenario_description').html(response.description);
                    $('#scenario_user').html(response.user);
                    $('#scenario_date').html(response.date);
                    $('#scenario_modified').html(response.modified);
                    $('#scenario_content').text(response.contents);
                    $('#scenario_public').text(response.is_public === true ? 'Yes':'No');

                    $('#delete_scenario_button').toggle(response.can_modify);
                    $('#edit_scenario_button').toggle(response.can_modify);
                    $('#toggle_public').toggle(response.can_modify);

                    var num_params = 0;
                    var params_in_scenario = response.params_in_scenario;
                    $.each(params_in_scenario, function(){
                        num_params = num_params+1;
                    });

                    if (num_params <= 0){
                        $('#scenario_parameters').append('<tr><td>No parameters defined (single run scenario).</td></tr>');
                    } else {
                        $('#scenario_parameters').append('<tr><th>Identifier</th><th>Description</th><th>Default Value(s)</th></tr>');
                        $.each(response.parameters, function(key,val) {
                            $('#scenario_parameters').append('<tr><td>@'+params_in_scenario[key]+'@</td><td>'+key+'</td><td>'+val+'</td></tr>');
                        });
                    }

                    prettyPrint();
                    $('#scenario_view_table').show();

                },
                error: function() {
                    alert('invalid status returned');
                },
                complete: function(){
                    // hide the loading
                    $('#waiting').hide();
                    // display the information table
                    $('#scenario_view_table').show();
                }
            });
        }

    });

    $('#edit-dialog').dialog({
        autoOpen:false,
        modal: true,
        height: 'auto' /*600*/,
        width: 'auto'/*700*/,
        resizable: false,
        open: function(){
            $('#scenario_editor_textarea').val($('#scenario_content').text())
        },
        buttons: { "Cancel": function() { $(this).dialog("close"); },
            "Save": function() {
                var scenario_id = $("#current_scenarios").val();

                var dialog = $(this);
                var new_scenario_text = $('#scenario_editor_textarea').val();
                $.ajax({
                    type: 'POST',
                    url: '/updateScenarioContents/',
                    data: {'scenario_id': scenario_id, 'scenario_contents':new_scenario_text},
                    success: function (response){
                        dialog.dialog("close");
                        if (response.success){
                            $('<div>').dialog({
                                modal:true,
                                resizable:false,
                                title: 'Successful Update',
                                open:function(){
                                    $(this).html('<p>The scenario contents were successfully updated</p>');
                                    $('#scenario_content').text(new_scenario_text);
                                    $('#scenario_modified').html(response.modified);
                                    prettyPrint();
                                }
                            });
                        } else {
                            $('<div>').dialog({
                                    modal:true,
                                    resizable:false,
                                    title: 'Failed Update',
                                    open:function(){
                                        $(this).css('background-color', '#FFCCCC');
                                        $(this).html('<p>New contents failed validation with message:</p><p>'+response.message+'</p><p>The scenario contents were not changed</p>');
                                    }
                            });
                        }
                    },
                    error: function() {
                        dialog.dialog("close");
                        $('<div>').dialog({
                            modal:true,
                            resizable:false,
                            title: 'Failed Update',
                            open:function(){
                                $(this).html('<p>The scenario contents were not updated. Please try again or contact the system administrator if this problem persists.</p>');
                            }
                        })

                    }
                });

            }

        }
    });

    $('#button_edit_scenario').attr('disabled','disabled').click(function(){
        $( "#edit-dialog" ).dialog( "open" );
    });

    /**
     * Handle click on "Delete Scenario" button for a scenario.
     */
    $('#button_delete_scenario').attr('disabled','disabled').click(function(){
        $('#delete-dialog' ).dialog("open");
    });

    $('#toggle_public').click( function(){
        $('#toggle-public-dialog').dialog("open");

    });

    $('#delete-dialog').dialog({
        autoOpen:false,
        modal: true,
        resizable: false,
        buttons: { "Cancel": function() { $(this).dialog("close"); },
            "OK": function() {
                window.location.href = '/deleteScenario/'+$("#current_scenarios").val()
                }
        }
    });

    $('#toggle-public-dialog').dialog({
        autoOpen:false,
        modal: true,
        resizable: false,
        buttons: { "Cancel": function() { $(this).dialog("close"); },
            "OK": function() {
                $.ajax({
                    type: 'GET',
                    url: '/togglePublicScenario/'+$("#current_scenarios").val(),
                    success: function(response) {
                        var displayText = response.is_public ? 'Yes':'No';
                        $('#scenario_public').text(displayText);
                        $('#toggle-public-dialog').dialog("close");

                    },
                    error: function() {
                        $('#toggle-public-dialog').dialog("close");
                        alert('invalid status returned');
                    }
                });
            }
        }
    });


    prettyPrint();


});

