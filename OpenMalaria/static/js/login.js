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
	//Set up the water mark on the input fields
	$("#userid_field").watermark("Username").keyup(function(event) {
        if (event.keyCode == 13) {
            $("#password_field").focus();
        }
    });

	$("#password_field").watermark("Password").keydown(function(event) {
        if (event.keyCode == 13) {
            $("#login_button").mousedown();
        }
    }).keyup(function(event) {
        if (event.keyCode == 13) {
            $("#password_field").blur();
            $("#login_button").click();
        }
    });
	
	//set up the color toggling for the login button
	$("#login_button").mousedown(function() {
		$(this).css({'background-color' : 'rgba(100,100,100,0.5)'});
	}).mouseup(function() {
		$(this).css({'background-color' : 'rgba(255,255,255,0.5)'});
	}).click(function() {
		$(this).css({'background-color' : 'rgba(255,255,255,0.5)'});
		handleLoginAttempt(); // This method is defined below
	});

    $("#crc_link").click( function (){
        window.location = "http://crc.nd.edu/";
    });

    $("#stphi_link").click( function (){
        window.location = "http://www.swisstph.ch/";
    });

    $("#jcu_link").click( function (){
        window.location = "http://www.jcu.edu.au/";
    });

    // Now fade in the login panel so that it is visible to the user
    $("#login_panel").fadeIn('slow', function(){
        //Do nothing but wait for interaction
    });

});
 
function handleLoginAttempt(){
    var password = $("#password_field").val();
    var user_id = $("#userid_field").val();

    if (password && user_id){
        $.ajax({
            type: 'POST',
            url: '/ajaxAuth/',
            data: {'uid': user_id, 'pwd':password, 'csrfmiddlewaretoken' : $('input[name="csrfmiddlewaretoken"]').val() },
            success: function(response) {
               if (response.url) {
                   $("#login_panel").fadeOut('fast', function(){
                       $("#navmenu").fadeIn('fast', function(){
                           window.location = response.url;
                       });
                   });
               } else {
                   shakeWithError(response.message);
               }
            },
            error: function(response) {
                shakeWithError('Login request failed! (Error: ' + $(response).statusCode+ ')');
            }
        });
 	} else {
        shakeWithError('Invalid username and/or password!');
 	}
}

function shakeWithError(error) {
    $("#login_panel").animate({left: '+=20'}, 70, function() {
        $("#login_panel").animate({left: '-=40'}, 140, function() {
            $("#login_panel").animate({left: '+=20'}, 70, function() {
                $("#login_error").text(error);
            });
        });
    });
}