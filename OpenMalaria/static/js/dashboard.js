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

$(document).ready(function(){
   // Browse through the progress bar to put the right color
    $('#logo_title').addClass('selected_menu');


    $('div.ui-progress').each(function(){
        //Retrieve the value
        var value = $(this).attr('data-value');

        // Get the associated color
        var color = Get_Color(value/100);

        // Set it
        $(this).css('background-color',color);
    });

    $('*[id*=show]:visible').click( function() {
        var table_id = $(this).parents('tr').attr('id');
        var components = table_id.split('_');
        var exp_num = components[components.length-1];

        $('.exp_details_'+exp_num).toggle();

    });

    $('[id^="cancel_link"]').click( function(event) {
        event.preventDefault();
        alert("Trying to cancel sim #: "+$(this).prop('title'));
        $.ajax({type: 'GET', url: '/cancelRun/'+$(this).prop('title'),
            //on success, populate the table values
            success: function() {
                $(this).hide();
            },
            //on error show an alert.
            error: function() {
                alert('An error occurred trying to cancel the simulation run.')
            }
        });


    });

    (function worker() {
        var num_exps = 1;
        $.ajax({
            url: '/getUserSimulationStatus/',
            success: function(response) {
                $.each(response.sims, function() {
                    var tmpId = this.id;
                    var tmpStatus = this.status;

                    if (tmpStatus > 0){
                        $('#sim_status_'+tmpId).attr('data-value', tmpStatus);
                        $('#sim_status_'+tmpId).width(tmpStatus+'%');
                        $('#sim_status_label_'+tmpId).text(tmpStatus+'%');
                        // Get the associated color
                        var color = Get_Color(tmpStatus/100);
                        // Set it
                        $('#sim_status_'+tmpId).css('background-color',color);
                    }
                    else if(tmpStatus == -1)
                    {
                        $('#sim_status_label_'+tmpId).text('Error');
                        $('#sim_status_label_'+tmpId).attr('title',this.message);
                    }
                });
//                alert(response.exps.length);
                num_exps = response.exps.length;
                $.each(response.exps, function() {
                    // Retrieve the info from the experiments table
                    var tmpId = this.id;
                    var percentage = this.status.percentage_done;
                    var total = this.status.total_simulations;
                    var failed = this.status.failed_simulations;
                    var completed = this.status.completed_simulations;

                    // Set the progress bar
                    if (percentage > 0){
                        $('#exp_status_'+tmpId).attr('data-value', percentage);
                        $('#exp_status_'+tmpId).width(percentage+'%');
                        $('#exp_status_label_'+tmpId).text(percentage+'%');
                        var color = Get_Color(percentage/100);
                        // Set it
                        $('#exp_status_'+tmpId).css('background-color',color);
                    }

                    // Set the other values
                    $('#total_'+tmpId).html(total);
                    $('#remaining_'+tmpId).html(total-failed-completed);
                    $('#completed_'+tmpId).html(completed);
                    $('#failed_'+tmpId).html(failed);
                });

            },
            complete: function() {
                // Schedule the next request when the current one's complete
                if (num_exps > 0) {
                    setTimeout(worker, 7000);
                }
            }
        });
    })();

});