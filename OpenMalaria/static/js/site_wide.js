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

$.extend({
    keys:    function(obj){
        var a = [];
        $.each(obj, function(k){ a.push(k) });
        return a;
    }
});

/* Set up the handlers for the dashboard view */
$(document).ready(function() {

    /* Add button effects to elements when clicked */
    $(".clickable").mousedown(function () {
        $(this).css ({'background-color' : 'rgba(100,100,100,0.5)'});
    }).mouseup(function () {
        $(this).css ({'background-color' : 'transparent'});
    });

    /* Defines expansion/contraction behavior for the menu bar */
    $("#navmenu_expand").click( function () {
        $(".nav_collapsible").each(function () {
            $(this).toggle();
        });
        var imgSrc = $(this).attr('src');
        if (imgSrc.indexOf('left') >= 0) {
            $(this).attr('src', '/static/img/expand-right.png');
        } else {
            $(this).attr("src", '/static/img/expand-left.png');
        }
    });

    /* assigns the dashboard button behavior */
    $("#logo_title").click( function () {
        window.location = '/dashboard/';
    });

    /* assigns the scenarios button behavior */
    $("#navmenu_scenarios").click( function () {
        window.location = '/scenarios/';
    });

    /* assigns the experiments button behavior */
    $("#navmenu_experiments").click( function () {
        window.location = '/experiments/';
    });

    /* assigns the experiments button behavior */
    $("#navmenu_results").click( function () {
        window.location = '/results/';
    });

    /* assigns the account button behavior */
    $("#navmenu_account").click( function () {
        window.location = '/account/';
    });

    /* assigns the logout button behavior */
    $("#navmenu_logout").click( function () {
        $("#navmenu").fadeOut('fast', function(){
            window.location = '/logout/';
        });
    });

    /* Handle close button on notification divs */
    $(".notification_close").click(function(){
        $(this).parent($('.notification')).hide();
    });


});


/*****************************************************************
 Function: Get_Color(float)
 Input: Double
 Returns: String (hex form: '#XXXXXX')
 Purpose: Pass in a float-type value to retrieve a corresponding
 color.  Value 0 starts at LimeGreen.  As the value approaches 7.5,
 the color gradually changes to yellow.  From 7.5 to 9, the color
 gradually changes to orange.  From 9 to 10, the color gradually
 changes to red.  Colors are compiled using Red, Green, and Blue
 values.  Because Green, Yellow, Orange and Red have no blue at
 all, "blue" always remains zero (0). Cap control is provided so
 no color value can be outside of the desired range, nor lower
 than zero/greater than 255.  Values range from 0-255. Possibility
 of 16,581,375 colors, though because blue is omitted, colors
 are reduced to 65,025 colors.  Calculations are based on the
 following chart:

 Value  Returned
 In   |  Color  |   R  |  G  |  B  |
 -------+---------+------+-----+-----|
 1   |LimeGreen|   0  | 200 |  0  |
 -------+---------+------+-----+-----|
 ~   |    ~    |   +  |  +  |  x  |
 -------+---------+------+-----+-----|
 .25  | Yellow  |  210 | 255 |  0  |
 -------+---------+------+-----+-----|
 ~   |    ~    |   +  |  -  |  x  |
 -------+---------+------+-----+-----|
 .1   | Orange  |  255 | 127 |  0  |
 -------+---------+------+-----+-----|
 ~   |    ~    |   x  |  -  |  x  |
 -------+---------+------+-----+-----|
 0   |   Red   |  255 |  0  |  0  |
 -------+---------+------+-----+-----|
 ****************************************************************/
function Get_Color(percentage)
{
    // adjust for opposite mapping (1 = lime green -> 0 = Red)
    percentage = 1 - percentage;

    // adjust percentage for 0-10
    var value = roundNumber((roundNumber(percentage, 2) * 10), 2);

    //initiate values for red, green, and blue
    var red = 0;
    var green = 0;
    var blue = 0;

    var return_color;

    //if the value passed in is at or lower than 7.5,
    //we adjust the green between 200 and 255;
    //red is adjusted between 0 and 210.
    if (value <= 7.5)
    {
        //calculate for green
        green = ((value * 7.33) + 200);
        if (green > 255)
            green = 255;
        if (green < 200)
            green = 200;

        //calculate for red
        red = (value * 28);
        if (red > 210)
            red = 210;
        if (red < 0)
            red = 0;

        //create a new color with our calculated values
        return_color = '#' + componentToHex(Math.floor(red)) + componentToHex(Math.floor(green)) + componentToHex(Math.floor(blue));
        //return our new color
    } else

    //if the value is less than 9 (but greater than 7.5 for the "if"
    //statement filtered those out), we adjust the red between 210
    //and 255, and the green between 255 and roughly 127 (technically
    //127.5, but who's gonna notice?)
    if (value <= 9)
    {
        //calculate for red
        red = ((value - 7.5) * 30) + 210;
        if (red > 255)
            red = 255;
        if (red < 210)
            red = 210;

        //calculate for green
        green = (255 - ((value - 7.5) * 85));
        if (green > 255)
            green = 255;
        if (green < 127)
            green = 127;

        //create a new color with our calculated values
        return_color = '#' + componentToHex(Math.floor(red)) + componentToHex(Math.floor(green)) + componentToHex(Math.floor(blue));
    } else {
    //if neither of the previous "if" statements ran, the value
    //passed in will be between 9 and 10.
    //at this point, red must be 255, and we just need to
    //adjust the green (to go from orange to red)

        //set red to 255
        red = 255;

        //calculate for green
        green = (255 - ((value - 8) * 127));
        if (green > 127)
            green = 127;
        if (green < 0)
            green = 0;

        //create a new color with our calculated values
        return_color = '#' + componentToHex(Math.floor(red)) + componentToHex(Math.floor(green)) + componentToHex(Math.floor(blue));
    }
    return return_color;
}

/**********************************************************************
 * Used for for converting integer values to Hex (0-16) maps to (0-F)
 * ********************************************************************/
function componentToHex(c) {
    var hex = c.toString(16);
    return hex.length == 1 ? "0" + hex : hex;
}

/**********************************************************************
 * Used for rounding decimal places.
 * Used as: roundNumber(number to round, number of decimal places);
 * Example: roundNumber(10.12345, 2)
 * 		- Returns: 10.12
 * ********************************************************************/
function roundNumber(num, dec) {
    return Math.round(num*Math.pow(10,dec))/Math.pow(10,dec);
}

function maskKeyPress(evt, mask) {
    var code, strKey;
    if (evt.keyCode) {
        code = evt.keyCode;
    } else if (evt.which) {
        code = evt.which;
    }
    if (evt.altKey || evt.ctrlKey ||  evt.metaKey){
        return true;
    }

    strKey = String.fromCharCode(code);

    return mask.test(strKey);
}
