// javascript functions
<!-- global variables -->
var months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
var temp_name;
var temp_choice;
var temp_importance;
var temp_category;
var temp_due_date;
var temp_due_time;
var temp_freq_int;
var temp_freq_choice;
var temp_id;
var update;
var remove_warning = -1;
var remove_alarm = -1;

<!-- format the date (Last Acknowledged Date or Due Date) -->
function formatDate (timeVal) {
    var year = timeVal.getFullYear();

    if (year == today.getFullYear()) {
        year = '';
    }
    else {
        year = ' ' + year;
    }

    var month = months[timeVal.getMonth()];

    var day = timeVal.getDate();
    if (day == 1 || day == 21 || day == 31) {
        day = day + 'st';
    }
    else if (day == 2 || day == 22) {
        day = day + 'nd';
    }
    else if (day == 3 || day == 23) {
        day = day + 'rd';
    }
    else {
        day = day + 'th';
    }

    var hour = timeVal.getHours();
    var meridiem = 'am';
    if (hour == 0) {
        hour = 12;
    }
    else if (hour > 11) {
        meridiem = 'pm';
    }
    if (hour > 12) {
        hour = hour - 12;
    }

    var minute = timeVal.getMinutes();
    if (minute < 10) {
        minute = '0' + minute;
    }

    return month + ' ' + day + year + ', ' + hour + ':' + minute + ' ' + meridiem;
}

<!-- parse the number, category, and id from a Link ID -->
function ParseID (link) {
    var short_id = link.substring(link.indexOf('-') + 1);
    var combo = link.substring(link.indexOf('link') + 4);

    this.id = (short_id.substring(short_id.indexOf('-') + 1)).slice(0, -1);
    this.num = combo.substring(0, combo.indexOf('-'));
    this.index = short_id.substring(0, short_id.indexOf('-'));
    this.full_id = link;
}

<!-- initialize the profile -->
function profileInit () {
    //document.getElementById('score').innerHTML = 'Score: ' + score;
    $("[id^='category").find('.ui-collapsible-heading-toggle').addClass('test-set');

    getTime();
}

<!-- get the Time Remaining -->
function getTime () {
    var now = new Date();

    for (var i = 0; i < task_count; i++) {
        formatTimeRemaining(due_date[i] - now, i);
    }

    var t = setTimeout(function(){getTime()}, 1000);
}

<!-- stats Time Remaining -->
function statsTimeRemaining (num) {
    //alert('Num: ' + num + '\nDue Date: ' + due_date[num]);
    var now = new Date();
    var timeVal = due_date[num] - now;
    var stat_time = $('#statTime');
    //alert(timeVal);

    // format the time remaining and run the function again
    if (tracking[num]) {
        //alert('SmartTRACK tracking[' + num + '] = ' + tracking[num]);
        if (stat_time.css('color') == 'rgb(51, 51, 51)') {
            stat_time.css('color', 'green');
        }
        else {
            defaultColor();
        }

        stat_time.html('&nbsp;SmartTRACK In Progress');
    }
    else if (timeVal < 1000) {
        //alert('Alarm tracking[' + num + '] = ' + tracking[num]);
        if (stat_time.css('color') == 'rgb(51, 51, 51)') {
            stat_time.css('color', 'rgb(255, 51, 51)');
        }
        else {
            defaultColor();
        }

        stat_time.html('&nbsp;0:00:00');
    }
    else {
        //alert('Regular tracking[' + num + '] = ' + tracking[num]);
        stat_time.html('&nbsp;' + formatTimer(timeVal));
    }

    //alert('setTimeout num: ' + num);
    update = setTimeout(function(){statsTimeRemaining(num)}, 1000);
}

<!-- format the Time Remaining -->
function formatTimeRemaining (timeVal, num) {
    var selector = $("[id^='link" + num + '-' + "']");
    var parse = new ParseID(selector.attr('id'));

    //alert('Task ' + num + ' has timeVal: ' + timeVal + ' and tracking: ' + tracking[num]);
    if (tracking[num] == 0 && timeVal < 1000) {
        //alert('change task ' + num + ' to red');
        changeColor(num, 2);

        if (past_due[num]) {
            past_due[num] = 0;

            setTimeout(function() {
                // AJAX create task
                $.ajax({
                    url : 'acknowledge/',
                    type : 'POST',
                    data : { id : parse.id,
                             type: 'time'
                    },

                    // successful response
                    success : function(json) {
                        //if (json.score != 0) {updateScore (json.score);}
                    },

                    // non-successful response
                    error : function(xhr,errmsg,err) {
                        console.log(xhr.status + ': ' + xhr.responseText); // log the error to the console
                        alert('acknowledge ajax failure');
                    }
                });
            }, num * 25);
        }
    }
    else if (tracking[num] == 0) {
        if (timeVal < 86400000) {
            //alert('change task ' + num + ' to yellow');
            //alert('ID of warning task: ' + form_id.attr('id'));
            changeColor(num, 1);
        }
        else {
            //alert('ID of non-warning/alarm tasks: ' + form_id);
            changeColor(num, 0);

            if (selector.hasClass('warning')) {
                selector.removeClass('warning');
            }
        }

        if (selector.hasClass('alarm')) {
            selector.removeClass('alarm');
        }


        if (remove_alarm == num) {
            var cat = $('#category' + parse.index).find('.ui-collapsible-heading-toggle');
            cat.removeClass('alarm-cat');

            if (remove_warning == num) {
                cat.addClass('test-set');
            }
            else {
                cat.addClass('warning-cat');
            }

            remove_alarm = -1;
        }

        if (remove_warning == num) {
            var cat = $('#category' + parse.index).find('.ui-collapsible-heading-toggle');
            cat.removeClass('warning-cat');

            if (cat.hasClass('alarm-cat') == false) {
                cat.addClass('test-set');
            }

            remove_warning = -1;
        }
    }
}

<!-- set the color to default if SmartTRACK is acknowledged/disabled -->
function defaultColor () {
    if ($('#statTime').css('color') != 'rgb(51, 51, 51)') {
        $('#statTime').css('color', 'rgb(51, 51, 51)');
    }
}

<!-- format the time remaining -->
function formatTimer (timeVal) {
    var w = Math.floor(timeVal / 604800000);
    var d = Math.floor((timeVal - (w * 604800000)) / 86400000);
    var h = Math.floor((timeVal - (w * 604800000) - (d * 86400000)) / 3600000);
    var m = Math.floor((timeVal - (w * 604800000) - (d * 86400000) - (h * 3600000)) / 60000);
    var s = Math.floor((timeVal - (w * 604800000) - (d * 86400000) - (h * 3600000) - (m * 60000)) / 1000);

    if (w == 0) {
        w = '';
    }
    else if (w == 1) {
        w = w + ' week, ';
    }
    else {
        w = w + ' weeks, ';
    }

    if (d == 0) {
        d = '';
    }
    else if (d == 1) {
        d = d + ' day, ';
    }
    else {
        d = d + ' days, ';
    }

    if (m < 10) {
        m = '0' + m;
    }

    if (s < 10) {
        s = '0' + s;
    }

    return w + d + h + ':' + m + ':' + s;
}

<!-- update the score -->
function updateScore (num) {
	score += num;
	var scoreStr = '' + score;
	var blank = '';

	for(var i = 0; i < (5 - scoreStr.length); i++) {
		blank = blank + ' ';
	}

	document.getElementById('score').innerHTML = 'Score: ' + blank + score;
}

<!-- change Time Remaining color to yellow if task has < 1 day remaining and red if task is overdue (0 == warning, 1 == alarm) -->
function changeColor (num, type) {
    var parse = new ParseID($("[id^='link" + num + '-' + "']").attr('id'));
    var index = $('#category' + parse.index).find('.ui-collapsible-heading-toggle');

    if (type == 0) {
        // No alarm/warning state
        //alert('Clear State -\nNum: ' + num + '\ntest-set: ' + index.hasClass('test-set') + '\nWarning: ' + index.hasClass('warning-cat') + '\nAlarm: ' + index.hasClass('alarm-cat'));
        if ((index.hasClass('test-set') != true) && (index.hasClass('warning-cat') != true) && (index.hasClass('alarm-cat') != true)) {
            //alert(index.attr('id'));
            $(index).addClass('test-set');
            //alert(temp_id);

            /*if (index == 'category0') {
                alert('this should not display...');
            }*/
        }
    }
    else if (type == 1) {
        // Warning state
        $("[id^='link" + num + '-' + "']").addClass('warning');

        if (index.hasClass('alarm-cat') != true) {
            index.removeClass('test-set').addClass('warning-cat');
            //alert('Category ' + index + ' has a warning.');
            //alert('Warning State -\nNum: ' + num + '\ntest-set: ' + index.hasClass('test-set') + '\nWarning: ' + index.hasClass('warning-cat') + '\nAlarm: ' + index.hasClass('alarm-cat'));
        }
    }
    else {
        // Alarm state
        //alert('Adding alarm for num ' + num);
        $("[id^='link" + num + '-' + "']").addClass('alarm');
        index.removeClass('test-set').addClass('alarm-cat');
        //alert('Alarm State -\nNum: ' + num + '\ntest-set: ' + index.hasClass('test-set') + '\nWarning: ' + index.hasClass('warning-cat') + '\nAlarm: ' + index.hasClass('alarm-cat'));
    }
}

// go back one page
function goBack() {
    window.history.back();
}

// check if the required form fields have data and enable the save button if so
function checkSave () {
    var name = document.getElementById('id_name').value.length;
    var due = document.getElementById('id_due_date').value.length;
    var frequency = document.getElementById('id_frequency_int').value.length;
    var choice_date = document.getElementById('id_choice_date').checked;
    var choice_frequency = document.getElementById('id_choice_frequency').checked;

    if (name < 1 || (choice_date && (due < 6)) || (choice_frequency && (frequency < 1))) {
        $('#taskSave').button('disable');
    }
    else {
        $('#taskSave').button('enable');
    }
}

// reset the form
function resetForm() {
    $('#id_category').selectmenu('enable');
    document.getElementById('taskForm').reset();
    $('#div_choice_date').hide();
    $('#div_choice_frequency').hide();
    //$('#id_due_date').removeClass("error");
    $('#modalTitle').html('Add Action');
    $('#taskSave').button('disable').changeButtonText('Add').button('option', 'icon', 'plus').button('refresh');
    $('#created_date').html('');

    setRadio();
}

function setRadio (button) {
    var smartTRACK = true;
    var date = false;
    var frequency = false;

    if (button == 'date') {
        smartTRACK = false;
        date = true;
    }
    else if (button == 'frequency') {
        smartTRACK = false;
        date = false;
        frequency = true;
    }

    $('#id_choice_smartTRACK').prop('checked', smartTRACK).checkboxradio('refresh');
    $('#id_choice_date').prop('checked', date).checkboxradio('refresh');
    $('#id_choice_frequency').prop('checked', frequency).checkboxradio('refresh');
}

// check if the entered frequency is a number
function isNumber(e) {
    e = (e) ? e : window.event;
    var charCode = (e.which) ? e.which : e.keyCode;

    if (charCode > 31 && (charCode < 48 || charCode > 57)) {
        return false;
    }
    return true;
}

// Jquery functions
$(document).on('pageinit', '#pageone, #pageabout, #pagesettings, #pagehome, #pagecategory, #pagepremade', function() {
    // swipe menu functionality
    $( document ).on( 'swipeleft swiperight', '#pageone, #pageabout, #pagesettings, #pagehome, #pagecategory, #pagepremade', function( e ) {
        // alert('swipe menu called');
        // We check if there is no open panel on the page because otherwise
        // a swipe to close the left panel would also open the right panel (and vice versa).
        // We do this by checking the data that the framework stores on the page element (panel: open).
        if ( $.mobile.activePage.jqmData( 'panel' ) !== 'open' ) {
            if ( e.type === 'swiperight'  ) {
                $( '#menu' ).panel( 'open' );
            } else if ( e.type === 'swipeleft' ) {
                $( '#menu' ).panel( 'close' );
            }
        }
    });

    // if a link is clicked open up the task stats popup
    $("[id^='link']").on('tap', function () {
        clearTimeout(update);
        var parse = new ParseID($(this).closest('a').attr('id'));

        $.ajax({
            url : 'stat_init/',
            type : 'POST',
            data : { id : parse.id,
                offset: offset
            },

            // successful response
            success : function(json) {
                $('#statTitle').html(json.name);
                $('#statId').html(parse.full_id);

                var last = new Date(json.last_year, json.last_month - 1, json.last_day, json.last_hour, json.last_minute - offset);
                var due = new Date(json.due_year, json.due_month - 1, json.due_day, json.due_hour, json.due_minute - offset);
                var created = new Date(json.created_year, json.created_month - 1, json.created_day, json.created_hour, json.created_minute - offset);

                if (json.total) {
                    $('#statLast').html('&nbsp;' + formatDate(last));
                }
                else {
                    $('#statLast').html('&nbsp;-');
                }

                if (tracking[parse.num]) {
                    $('#statDue').html('&nbsp;-');
                }
                else {
                    $('#statDue').html('&nbsp;' + formatDate(due));
                }

                $('#statCreated').html('&nbsp;' + formatDate(created));
                $('#statTotal').html('&nbsp;' + json.total);
                $('#statTrack').html('&nbsp;' + json.track);
                $('#statFrequency').html('&nbsp;' + json.frequency);

                // assign values to the temp variables in case 'Edit Task' is clicked
                temp_category = json.category;
                temp_name = json.name;
                temp_choice = json.choice;
                temp_importance = json.importance;
                temp_id = parse.full_id;

                if (temp_choice == 1) {
                    temp_due_time = json.due_time;
                    temp_due_date = json.due_date;
                }
                else if (temp_choice == 2) {
                    temp_freq_choice = json.freq_choice;
                    temp_freq_int = json.freq_int;
                }

                statsTimeRemaining(parse.num);
                $('#statModal').popup('open');
            },

            // non-successful response
            error : function(xhr,errmsg,err) {
                console.log(xhr.status + ': ' + xhr.responseText); // log the error to the console
                alert('stat_init ajax failure');
            }
        });
    });

    $('#statEdit').on('click', function () {
        $('#statModal').popup('close');
        clearTimeout(update);
        defaultColor();

        $('#modalTitle').html("Edit '" + temp_name + "'");
        $('#modalId').html(temp_id);
        $('#taskSave').button('enable').changeButtonText("Save").button( "option", "icon", "edit" ).button('refresh');

        if (temp_choice == 1) {
            $("#div_choice_date").show();

            document.getElementById('id_due_date').value = temp_due_date;

            var due_time = $('#id_due_time');
            due_time.val(temp_due_time).attr('selected', true).siblings('option').removeAttr('selected');
            due_time.selectmenu("refresh", true);

            $('#id_due_date').attr('disabled', false);
            due_time.attr('disabled', false);

            setRadio('date');
        }
        else if (temp_choice == 2) {
            $("#div_choice_frequency").show();

            document.getElementById('id_frequency_int').value = temp_freq_int;

            var frequency = $('#id_frequency_choice');
            frequency.val(temp_freq_choice).attr('selected', true).siblings('option').removeAttr('selected');
            frequency.selectmenu("refresh", true);

            $('#id_frequency_int').attr('disabled', false);
            frequency.attr('disabled', false);

            setRadio('frequency');
        }

        // populate the form with the correct initial values
        document.getElementById('id_name').value = temp_name;

        var cat = $('#id_category');
        cat.val(temp_category).attr('selected', true).siblings('option').removeAttr('selected');
        cat.selectmenu('disable');
        cat.selectmenu("refresh", true);

        var importance = $('#id_importance');
        importance.val(temp_importance).attr('selected', true).siblings('option').removeAttr('selected');
        importance.selectmenu("refresh", true);

        $('#taskModal').popup('open');
    });


    // if a link is held for one second bring up the acknowledge task popup
    $("[id^='link']").on('taphold', function () {
        var parse = new ParseID($(this).closest('a').attr('id'));
        clearTimeout(update);

        $('#ackSave').button('enable');
        //$("#ackCancel").button('enable');

        // AJAX acknowledge init task
        $.ajax({
            url : 'acknowledge_init/',
            type : 'POST',
            data: { id : parse.id },

            // successful response
            success : function(json) {
                if (json.en_SmartTRACK) {
                    $('#div_id_omit').show();
                }
                else {
                    $('#div_id_omit').hide();
                }

                $('#ackTitle').html("Acknowledge '" + json.name + "'?");
                $('#ackTime').html('&nbsp;' + formatDate(new Date()));
                $('#ackId').html(parse.full_id);
                //$('#ackLast').html(json.last_year);
                var last = new Date(json.last_year, json.last_month - 1, json.last_day, json.last_hour, json.last_minute - offset);
                var due = new Date(json.due_year, json.due_month - 1, json.due_day, json.due_hour, json.due_minute - offset);
                $('#ackLast').html('&nbsp;' + formatDate(last));
                $('#ackDue').html('&nbsp;' + formatDate(due));

                $('#ackModal').popup('open');
            },

            // non-successful response
            error : function(xhr,errmsg,err) {
                console.log(xhr.status + ': ' + xhr.responseText); // log the error to the console
                alert('acknowledge_init ajax failure');
            }
        });
    });

    // Ackowledge Task
    $('#ackSave').on('click', function() {
        var parse = new ParseID($('#ackId').html());
        var omit = document.getElementById('id_omit').checked;

        // AJAX acknowledge
        $.ajax({
            url: 'acknowledge/',
            type: 'POST',
            data: {
                id: parse.id,
                omit: omit,
                type: 'button'
            },

            // successful response
            success: function (json) {
                due_date[parse.num] = new Date(json.due_year, json.due_month - 1, json.due_day, json.due_hour, json.due_minute - offset);
                past_due[parse.num] = 1;
                tracking[parse.num] = 0;
                //defaultColor();

                if (json.warning) {
                    remove_warning = parse.num;
                }

                if (json.alarm) {
                    remove_alarm = parse.num;
                }

                // TODO - if the due date changed enough, move it to a new place in the listview list
                //alert('This has changed: ' + json.changed);
                //alert('Position: ' + json.position);
                //alert('Category Num: ' + json.link_number);
                //alert('Num: ' + parse.num);
                //alert('Id: ' + json.id);
                //alert('Name: ' + json.name);

                if (json.changed) {
                    //alert('position has changed');
                    var position_array = [];

                    $("[id*='-" + json.link_number + "-']").each(function (index) {
                        //alert(index + ': ' + $(this).attr('id'));
                        position_array.push($(this).attr('id'));
                    });

                    var temp_pos = json.position;
                    var start_pos = json.position_start;

                    //alert('End Position: ' + temp_pos + '\nStart Position: ' + start_pos);

                    var temp_name1 = json.name;
                    var temp_id1 = json.id;
                    var temp_num1 = parse.num;
                    var temp_index1 = json.link_number;
                    var temp_name2 = '';
                    var temp_id2 = -1;
                    var temp_num2 = -1;
                    var temp_index2 = -1;
                    var length = position_array.length;

                    //$('#ackModal').popup('close');
                    //alert('before for');
                    for (var i = temp_pos; i >= start_pos; i--) {
                        var parse_now = new ParseID(position_array[i]);

                        if ((i - 1) >= start_pos) {
                            temp_name2 = ($('#' + parse_now.full_id).find('.link-header').html()).trim();
                            temp_id2 = parse_now.id;
                            temp_num2 = parse_now.num;
                            temp_index2 = parse_now.index;
                        }

                        //alert('Name1: ' + temp_name1 + '\nNum1: ' + temp_num1 + '\nIndex1: ' + temp_index1 + '\nID1: ' + temp_id1 + '\nName2: ' + temp_name2 + '\nID2: ' + temp_num2 + '\nIndex2: ' + temp_index2 + temp_id2 + '\nNum2: ');

                        $('#' + parse_now.full_id).find('.link-header').html(temp_name1);
                        $('#' + parse_now.full_id).removeClass('warning').removeClass('alarm').attr('id', 'link' + temp_num1 + '-' + temp_index1 + '-' + temp_id1 + 'k');

                        temp_name1 = temp_name2;
                        temp_id1 = temp_id2;
                        temp_num1 = temp_num2;
                        temp_index1 = temp_index2;
                    }
                }

                $('#ackModal').popup('close');
            },

            // non-successful response
            error: function (xhr, errmsg, err) {
                console.log(xhr.status + ': ' + xhr.responseText); // log the error to the console
                alert('acknowledge ajax failure');
            }
        });
    });


    // form - custom task category ajax request
    $('#id_task_category').on('change', function(e) {
        var cat = $('#id_task_category').val();

        // AJAX acknowledge
        $.ajax({
            url: 'form_category/',
            type: 'POST',
            data: {
                category : cat
            },

            // successful response
            success: function (json) {
                var newOption = '';
                var output = '';

                for (var entry in json) {
                    output += 'key: ' + entry + ' | value: ' + json[entry] + '\n';
                    newOption += "<option value='" + entry + "'>" + json[entry] + '</option>';
                }

                $('#id_task_name').empty().append(newOption).val('').trigger('refresh');
                $('#id_task_name').prop('selectedindex',0).selectmenu('refresh');
                $('#id_category').selectmenu('open');
                },

                // non-successful response
                error: function (xhr, errmsg, err) {
                    console.log(xhr.status + ': ' + xhr.responseText); // log the error to the console
                    alert('form_category ajax failure');
                }
            });
    });

    // form - custom task name ajax request
    $('#id_task_name').on('change', function() {
        $.ajax({
            url: 'form_name/',
            type: 'POST',
            data: {
                position : $('#id_task_name').find(':selected').val(),
                category : $('#id_task_category').val(),
                offset : new Date().getTimezoneOffset()
            },

            // successful response
            success: function (json) {
                $('#id_name').val(json.name);
                $('#premadeId').val(json.id);

                var cat = $('#id_category');
                cat.val(json.category).attr('selected', true).siblings('option').removeAttr('selected');
                cat.selectmenu('refresh', true);

                var importance = $('#id_importance');
                importance.val(json.importance).attr('selected', true).siblings('option').removeAttr('selected');
                importance.selectmenu('refresh', true);

                if (json.choice == 0) {
                    setRadio();

                    $('#div_choice_date').hide();
                    $('#div_choice_frequency').hide();
                }
                else if (json.choice == 1) {
                    $('#div_choice_date').show();
                    $('#div_choice_frequency').hide();

                    setRadio('date');

                    document.getElementById('id_due_date').value = json.due_date;

                    var due_time = $('#id_due_time');
                    due_time.val(json.due_time).attr('selected', true).siblings('option').removeAttr('selected');
                    due_time.selectmenu('refresh', true);
                }
                else if (json.choice == 2) {
                    $('#div_choice_date').hide();
                    $('#div_choice_frequency').show();

                    setRadio('frequency');

                    document.getElementById('id_frequency_int').value = json.frequency_int;

                    var frequency = $('#id_frequency_choice');
                    frequency.val(json.frequency_choice).attr('selected', true).siblings('option').removeAttr('selected');
                    frequency.selectmenu('refresh', true);
                }

                checkSave();
                $('#premadeSave').button('enable');
            },

            // non-successful response
            error: function (xhr, errmsg, err) {
                console.log(xhr.status + ': ' + xhr.responseText); // log the error to the console
                alert('form_name ajax failure');
            }
        });
    });

    // clear values after cancel and reset the form CSS
    $('#addCancel').on('click', function() {
        $('#taskModal').popup('close');
        resetForm();
    });

    $('#ackCancel').on('click', function() {
        $('#ackModal').popup('close');
    });

    $('#statCancel').on('click', function() {
        clearTimeout(update);
        $('#statModal').popup('close');
        defaultColor();
    });

    $('#id_due_date').on('select', function() {
        //alert('due date changed!');
        checkSave();
    });

    /*$("#id_due_date").datepicker({
        alert('date picked');
    });*/

    // disable the create/edit save button until all necessary fields have values
    $('#id_name, #id_due_date, #id_frequency_int').bind('keyup focusout', function() {
        checkSave();
    });

    $('#id_category_custom').bind('keyup focusout', function() {
        length = document.getElementById('id_category_custom').value.length;

        if (length > 0) {
            $('#catSave').button('enable');
        }
        else {
            $('#catSave').button('disable');
        }
    });

    $("input[name^='custom']").on('change', function () {
        $('#catSave').button('enable');
    });

    // show the SmartTRACK, Date, or Frequency div
    $("input[id^='id_choice']").on('change', function() {
        if ($('#id_choice_date').prop('checked')) {
            $('#div_choice_frequency').hide();
            $('#div_choice_date').show();
        }
        else if ($('#id_choice_frequency').prop('checked')) {
            $('#div_choice_date').hide();
            $('#div_choice_frequency').show();
        }
        else {
            $('#div_choice_frequency').hide();
            $('#div_choice_date').hide();
        }

        checkSave();
    });

    // create_task save on submit
    $('#taskSave').on('click', function(e) {
        e.preventDefault();

        var parse = new ParseID($('#modalId').html());
        var title_name = $('#modalTitle').html().substring(0, 1);
        var data = new FormData($('#taskForm').get(0));

        data.append('id', parse.id);
        data.append('num', parse.num);
        data.append('offset', offset);

        if (title_name == 'A') {
            data.append('type', 'create');
        }
        else {
            data.append('type', 'edit');
        }

        //failhere();

        // AJAX edit task
        $.ajax({
            url : 'create_task/',
            type : 'POST',
            data: data,
            processData: false,
            contentType: false,

            // successful response
            success : function(json) {
                //alert('success?');
                if (json.new_category) {
                    //alert('time to redirect');
                    // do your redirect
                    $('#taskModal').popup('close');
                    location.replace('http://localhost/profile/');
                }
                else {
                    if (json.validation_error) {
                        alert('Create Validation Error');
                        if (json.date) {
                            alert('date is incorrect');
                            $('#id_due_date').addClass('error');
                            $('#div_id_due_date').effect('bounce', 'slow');
                        }
                    }
                    else if (json.type == 'create') {
                        due_date.push(new Date(json.due_year, json.due_month - 1, json.due_day, json.due_hour, json.due_minute - offset));
                        past_due.push(1);

                        if (json.tracking) {
                            tracking.push(1);
                        }
                        else {
                            defaultColor();
                            tracking.push(0);
                        }

                        var link = "<li class='task-class'><a id='link" + 0 + "-" + json.link_number + "-" + 0 + "k' href='#'><div class='link-header'>" + 'placeholder' + "</div></a></li>";

                        $('#list' + json.link_number).append(link).listview('refresh');

                        //var position = json.position;
                        var position_array = [];

                        $("[id*='-" + json.link_number + "-']").each(function(index) {
                            //alert(index + ': ' + $(this).attr('id'));
                            position_array.push($(this).attr('id'));
                        });

                        var temp_pos = json.position;

                        /*for (var i = 0; i < position_array.length; i++) {
                            if (position_array[i].includes('-' + json.position + 'k')) {
                                temp_pos = i;
                            }
                        }*/

                        var temp_name1 = json.name;
                        var temp_id1 = json.id;
                        var temp_num1 = json.list_number;
                        var temp_index1 = json.link_number;
                        var temp_name2 = '';
                        var temp_id2 = -1;
                        var temp_num2 = -1;
                        var temp_index2 = -1;
                        var length = position_array.length;

                        //alert('before for');
                        for (var i = temp_pos; i < length; i++) {
                            var parse_now = new ParseID(position_array[i]);

                            if ((i + 1) < length) {
                                //alert('Iteration: ' + i);
                                //var parse_next = new ParseID(position_array[i + 1]);
                                //alert(parse_now.id);
                                temp_name2 = ($('#' + parse_now.full_id).find('.link-header').html()).trim();
                                temp_id2 = parse_now.id;
                                temp_num2 = parse_now.num;
                                temp_index2 = parse_now.index;
                            }

                            //alert('Name1: ' + temp_name1 + '\nNum1: ' + temp_num1 + '\nIndex1: ' + temp_index1 + '\nID1: ' + temp_id1 + '\nName2: ' + temp_name2 + '\nID2: ' + temp_num2 + '\nIndex2: ' + temp_index2 + temp_id2 + '\nNum2: ');

                            $('#' + parse_now.full_id).find('.link-header').html(temp_name1);
                            $('#' + parse_now.full_id).removeClass('warning').removeClass('alarm').attr('id', 'link' + temp_num1 + '-' + temp_index1 + '-' + temp_id1 + 'k');

                            temp_name1 = temp_name2;
                            temp_id1 = temp_id2;
                            temp_num1 = temp_num2;
                            temp_index1 = temp_index2;
                        }

                        // rebind the acknowledge pop-up
                        $("[id^='link']").off('taphold').on('taphold', function () {
                            var parse = new ParseID($(this).closest('a').attr('id'));
                            clearTimeout(update);

                            $('#ackSave').button('enable');
                            //$("#ackCancel").button('enable');

                            // AJAX acknowledge init task
                            $.ajax({
                                url : 'acknowledge_init/',
                                type : 'POST',
                                data: { id : parse.id },

                                // successful response
                                success : function(json) {
                                    if (json.en_SmartTRACK) {
                                        $('#div_id_omit').show();
                                    }
                                    else {
                                        $('#div_id_omit').hide();
                                    }

                                    $('#ackTitle').html("Acknowledge '" + json.name + "'?");
                                    $('#ackTime').html('&nbsp;' + formatDate(new Date()));
                                    $('#ackId').html(parse.full_id);
                                    //$('#ackLast').html(json.last_year);
                                    var last = new Date(json.last_year, json.last_month - 1, json.last_day, json.last_hour, json.last_minute - offset);
                                    var due = new Date(json.due_year, json.due_month - 1, json.due_day, json.due_hour, json.due_minute - offset);
                                    $('#ackLast').html('&nbsp;' + formatDate(last));
                                    $('#ackDue').html('&nbsp;' + formatDate(due));

                                    $('#ackModal').popup('open');
                                },

                                // non-successful response
                                error : function(xhr,errmsg,err) {
                                    console.log(xhr.status + ': ' + xhr.responseText); // log the error to the console
                                    alert('acknowledge_init ajax failure');
                                }
                            });
                        });

                        // rebind the stats pop-up
                        $("[id^='link']").off('tap').on('tap', function () {
                            var parse = new ParseID($(this).closest('a').attr('id'));

                            $.ajax({
                                url : 'stat_init/',
                                type : 'POST',
                                data : { id : parse.id,
                                    offset: offset
                                },

                                // successful response
                                success : function(json) {
                                    $('#statTitle').html(json.name);
                                    $('#statId').html(parse.full_id);

                                    var last = new Date(json.last_year, json.last_month - 1, json.last_day, json.last_hour, json.last_minute - offset);
                                    var due = new Date(json.due_year, json.due_month - 1, json.due_day, json.due_hour, json.due_minute - offset);
                                    var created = new Date(json.created_year, json.created_month - 1, json.created_day, json.created_hour, json.created_minute - offset);

                                    if (json.total) {
                                        $('#statLast').html('&nbsp;' + formatDate(last));
                                    }
                                    else {
                                        $('#statLast').html('&nbsp;-');
                                    }

                                    if (tracking[parse.num]) {
                                        $('#statDue').html('&nbsp;-');
                                    }
                                    else {
                                        $('#statDue').html('&nbsp;' + formatDate(due));
                                    }

                                    $('#statCreated').html('&nbsp;' + formatDate(created));
                                    $('#statTotal').html('&nbsp;' + json.total);
                                    $('#statTrack').html('&nbsp;' + json.track);
                                    $('#statFrequency').html('&nbsp;' + json.frequency);

                                    // assign values to the temp variables in case 'Edit Task' is clicked
                                    temp_category = json.category;
                                    temp_name = json.name;
                                    temp_choice = json.choice;
                                    temp_importance = json.importance;
                                    temp_id = parse.full_id;

                                    if (temp_choice == 1) {
                                        temp_due_time = json.due_time;
                                        temp_due_date = json.due_date;
                                    }
                                    else if (temp_choice == 2) {
                                        temp_freq_choice = json.freq_choice;
                                        temp_freq_int = json.freq_int;
                                    }

                                    statsTimeRemaining(parse.num);
                                    $('#statModal').popup('open');
                                },

                                // non-successful response
                                error : function(xhr,errmsg,err) {
                                    console.log(xhr.status + ': ' + xhr.responseText); // log the error to the console
                                    alert('stat_init ajax failure');
                                }
                            });
                        });
                        //alert(link);
                        //alert(num);
                        //alert(due_date[num]);

                        //document.getElementById('due_date' + num).innerHTML = formatDate(due);


                        //document.getElementById('timer' + num).innerHTML = '&lrm;' + formatTimeRemaining(due_date[num] - now, num);
                        /*var now = new Date();
                        $('#timer' + num).html('&lrm;' + formatTimeRemaining(due_date[num] - now, num));
                        $('#due_date' + num).html(formatDate(due_date[num]));

                        //$('#' + full_id).closest('.header').html(json.name);
                        //$('#' + full_id).find('.inline').html(json.frequency_formatted);
                        $('#' + full_id).find('.header').html(json.name);
                        //alert(json.frequency_formatted);
                        $('#' + full_id).find('.inline').html(json.frequency);*/

                        //var $doc = document.getElementById(json.count + '-' + json.id);


                        /*$doc.cells[$en[0]].innerHTML = json.name;
                         due_date[json.count] = new Date(json.due_year, json.due_month - 1, json.due_day, json.due_hour, json.due_minute - offset);
                         if (enable[3]) {document.getElementById('due_date' + json.count).innerHTML = formatDate(due_date[json.count]);}
                         if (enable[4]) {$doc.cells[$en[4]].innerHTML = json.frequency_formatted;}
                         if (enable[5]) {$doc.cells[$en[5]].innerHTML = json.category;}
                         if (enable[6]) {$doc.cells[$en[6]].innerHTML = json.importance_formatted;}

                         document.getElementById('timer' + json.count).innerHTML = formatTimeRemaining(due_date[json.count] - new Date(), json.count);*/
                        //$('#taskModal').popup('close');
                    }
                    else if (json.type == 'edit') {
                        $('#' + parse.full_id).find('.link-header').html(json.name);
                        due_date[parse.num] = new Date(json.due_year, json.due_month - 1, json.due_day, json.due_hour, json.due_minute - offset);
                        past_due[parse.num] = 1;

                        if (json.tracking) {
                            tracking[parse.num] = 1;
                        }
                        else {
                            tracking[parse.num] = 0;
                        }

                        if (json.warning) {
                            remove_warning = parse.num;
                        }

                        if (json.alarm) {
                            remove_alarm = parse.num;
                        }

                        if (json.changed) {
                            //alert('position has changed');
                            var position_array = [];

                            $("[id*='-" + json.link_number + "-']").each(function (index) {
                                //alert(index + ': ' + $(this).attr('id'));
                                position_array.push($(this).attr('id'));
                            });

                            var temp_pos = json.position;
                            var start_pos = json.position_start;

                            alert('End Position: ' + temp_pos + '\nStart Position: ' + start_pos);

                            var temp_name1 = json.name;
                            var temp_id1 = json.id;
                            var temp_num1 = parse.num;
                            var temp_index1 = json.link_number;
                            var temp_name2 = '';
                            var temp_id2 = -1;
                            var temp_num2 = -1;
                            var temp_index2 = -1;
                            var length = position_array.length;

                            //$('#ackModal').popup('close');
                            //alert('before for');

                            if (start_pos < temp_pos) {
                                for (var i = temp_pos; i >= start_pos; i--) {
                                    var parse_now = new ParseID(position_array[i]);

                                    if ((i - 1) >= start_pos) {
                                        temp_name2 = ($('#' + parse_now.full_id).find('.link-header').html()).trim();
                                        temp_id2 = parse_now.id;
                                        temp_num2 = parse_now.num;
                                        temp_index2 = parse_now.index;
                                    }

                                    //alert('Name1: ' + temp_name1 + '\nNum1: ' + temp_num1 + '\nIndex1: ' + temp_index1 + '\nID1: ' + temp_id1 + '\nName2: ' + temp_name2 + '\nID2: ' + temp_num2 + '\nIndex2: ' + temp_index2 + temp_id2 + '\nNum2: ');
                                    $('#' + parse_now.full_id).find('.link-header').html(temp_name1);
                                    $('#' + parse_now.full_id).removeClass('warning').removeClass('alarm').attr('id', 'link' + temp_num1 + '-' + temp_index1 + '-' + temp_id1 + 'k');

                                    temp_name1 = temp_name2;
                                    temp_id1 = temp_id2;
                                    temp_num1 = temp_num2;
                                    temp_index1 = temp_index2;
                                }
                            }
                            else {
                                for (var i = temp_pos; i < start_pos; i++) {
                                    alert('start_pos: ' + start_pos + '> end_pos: ' + temp_pos);
                                    var parse_now = new ParseID(position_array[i]);

                                    if ((i + 1) < start_pos) {
                                        //alert('Iteration: ' + i);
                                        //var parse_next = new ParseID(position_array[i + 1]);
                                        //alert(parse_now.id);
                                        temp_name2 = ($('#' + parse_now.full_id).find('.link-header').html()).trim();
                                        temp_id2 = parse_now.id;
                                        temp_num2 = parse_now.num;
                                        temp_index2 = parse_now.index;
                                    }

                                    //alert('Name1: ' + temp_name1 + '\nNum1: ' + temp_num1 + '\nIndex1: ' + temp_index1 + '\nID1: ' + temp_id1 + '\nName2: ' + temp_name2 + '\nID2: ' + temp_num2 + '\nIndex2: ' + temp_index2 + temp_id2 + '\nNum2: ');

                                    $('#' + parse_now.full_id).find('.link-header').html(temp_name1);
                                    $('#' + parse_now.full_id).removeClass('warning').removeClass('alarm').attr('id', 'link' + temp_num1 + '-' + temp_index1 + '-' + temp_id1 + 'k');

                                    temp_name1 = temp_name2;
                                    temp_id1 = temp_id2;
                                    temp_num1 = temp_num2;
                                    temp_index1 = temp_index2;
                                }
                            }
                        }
                    }
                }

                $('#taskModal').popup('close');
                resetForm();
            },

            // non-successful response
            error : function(xhr,errmsg,err) {
                console.log(xhr.status + ': ' + xhr.responseText); // log the error to the console
                alert('create_task ajax error');
            }
        });
    });


    // Cookies, CSRF tokens, and same origin validation
    // get cookie with a given name
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
	
	// csrf token 
    var csrftoken = getCookie('csrftoken');

    /*
    The functions below will create a header with csrftoken
    */

	// these HTTP methods do not require CSRF protection
    function csrfSafeMethod(method) {
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
	
	// test that a given url is a same-origin URL.  URL could be relative or scheme relative or absolute
    function sameOrigin(url) {
        // test that a given url is a same-origin URL
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
    }

	// send the token to same-origin, relative URLs only.  Send the token only if the method warrants CSRF protection (Using the CSRFToken value acquired earlier)
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
                xhr.setRequestHeader('X-CSRFToken', csrftoken);
            }
        }
    });

    $('#addContent').bind('click', function () {
        var data = [{'id':1, 'start':'2011-10-29T13:15:00.000+10:00', 'end':'2011-10-29T14:15:00.000+10:00', 'title':'Meeting'}];

        //alert('changed to edit');
        var output = '';
        //iterate through the data using $.each()
        $.each(data, function(index, value){
            //add each value to the output buffer
            output += '<li>' + value.title + ' (Added using $.each())</li>';
        });

        //iterate through the data using for()
        for (key in data) {
            output += '<li>' + data[key].title + ' (Added using for())</li>';
        }

        output = "<li class='task-class'><a id='link8-4-33' href='#'><div class='link-header'>Dynamically added link</div></a></li>";

        //now append the buffered output to the listview and either refresh the listview or create it (meaning have jQuery Mobile style the list)
        //$('#listview').append(output).listview('refresh');//or if the listview has yet to be initialized, use `.trigger('create');` instead of `.listview('refresh');

        //var content = "<div data-role='collapsible' id='set" + 17 + "'><h3>Section " + 17 + "</h3><p>I am the collapsible content in a set so this feels like an accordion. I am hidden by default because I have the 'collapsed' state; you need to expand the header to see me.</p></div>";
       
        var content = "<div data-role='collapsible' id='set" + 22 + "'><h3>Section " + 22 + "</h3><p>I am the collapsible content in a set so this feels like an accordion. I am hidden by default because I have the 'collapsed' state; you need to expand the header to see me.</p></div>";
        content = "<div id='category14' data-role='collapsible' data-inset='false' data-collapsed-icon='arrow-r' data-expanded-icon='arrow-d'><h1><div class='ui-li-count'>14</div>Dynamically added category</h1></div>";

        var cat = "<div id='category25' data-role='collapsible' data-inset='false' data-collapsed-icon='arrow-r' data-expanded-icon='arrow-d'><h1><div class='ui-li-count'>14</div>Dynamo</h1><ul id='list25' data-role='listview'></ul></div>";

        var link = "<ul id='list25' data-role='listview'><li class='task-class'><a id='link8-4-33' href='#'><div class='link-header'>Dynamically2 added link</div></a></li></ul>";

        var link2 = "<li class='task-class'><a id='link8-4-33' href='#'><div class='link-header'>Dynamically added link</div></a></li>";

        var link3 = "<li class='task-class'>test link</li>";
        //$('#link3-0-16').remove();
        //$('#list0').append(output).listview('refresh');

        $('#category2').after(cat);
        $('div[data-role=collapsible]').collapsible();
        $('#category25').find('.ui-collapsible-heading-toggle').addClass('test-set');
        //$('div[data-role=listview]').listview();
        //$('div[data-role=listview]').listview('refresh');

        $('#listview').append(link3).listview('refresh');

        /*$('#list25').append(link3);
        alert('first');
        $('#list25').trigger('create');
        //$('#list25').listview('refresh');
        $('ul').listview('refresh');
        $('div[data-role=listview]').listview('refresh');*/

        //$('#category25').append(link);
        //$('div[data-role=collapsible]').collapsible();
        //$('div[data-role=listview]').listview();

        /*$('#list25').append(link2).trigger('create');
        $('div[data-role=listview]').trigger('create');
        $('div[data-role=listview]').listview();
        $('div[data-role=listview]').listview('refresh');
        $('div[data-role=collapsible]').collapsible();*/
        //alert('done');

        /*$('#6-3-12').find('li').after(output);
        $('#6-3-12').after(output);
        $('#6-3-12').closest('li').after(output);
        $('#list3').append(output).listview( 'refresh' );
        $('#list3').listview( 'refresh' );
        alert('list done');
        //$('#mainSet').append( content ).collapsibleset('refresh');
        //$('category14').find('.ui-collapsible-heading-toggle').addClass('test-set');
        //alert('done');
        $('#addContent').append( content ).collapsibleset( 'refresh' );
        $('#set17').collapsibleset( 'refresh' );
        //alert('done0');
        $('#category10').collapsible( 'refresh' );
        //alert('first');
        $('#category11').collapsibleset('refresh');
        $('#category12').collapsibleset('refresh');
        alert('done1');
        $('#category14').collapsibleset('refresh');
        alert('done2');*/
        //$('#category2').append( content ).collapsibleset('refresh');
    });

    $('#category25').on('click', function () {
       alert('clicked');
    });

    $('#addList').bind('click', function () {
        var data = [{"id":1, "start":"2011-10-29T13:15:00.000+10:00", "end":"2011-10-29T14:15:00.000+10:00", "title":"Meeting"}];

        var output = '';
        //iterate through the data using $.each()
        $.each(data, function(index, value){
            //add each value to the output buffer
            output += '<li>' + value.title + ' (Added using $.each())</li>';
        });

        //iterate through the data using for()
        for (key in data) {
            output += '<li>' + data[key].title + ' (Added using for())</li>';
        }

        var link = "<li class='task-class'><a id='link8-4-33' href='#'><div class='link-header'>Dynamically added link</div></a></li>";
        var cat = "<div id='category25' data-role='collapsible' data-inset='false' data-collapsed-icon='arrow-r' data-expanded-icon='arrow-d'><h1><div class='ui-li-count'>14</div>Dynamo</h1><ul id='list25' data-role='listview'></ul></div>";

        $('#category2').after(cat);
        $('div[data-role=collapsible]').collapsible();
        $('#category25').find('.ui-collapsible-heading-toggle').addClass('test-set');

        $("[id*='-0-']").each(function(index) {
            alert(index + ': ' + $(this).attr('id'));
        });

        /*$('li').each(function(index) {
            alert(index + ': ' + $(this).text());
        });*/

        //now append the buffered output to the listview and either refresh the listview or create it (meaning have jQuery Mobile style the list)
        //$('#listview2').append(link).listview('refresh');//or if the listview has yet to be initialized, use `.trigger('create');` instead of `.listview('refresh');`
        $('#list25').append(link).trigger('create');//or if the listview has yet to be initialized, use `.trigger('create');` instead of `.listview('refresh');`
    });


    $("#refreshUpdateButton").on("click", function(event, ui) {
        //alert('refresh clicked');
        //console.log("refreshUpdateButton");

        var versions = ["0.3", "0.4", "0.5"];

        for (var i=0; i < versions.length; i += 1) {
            $("#updateVersionsList").append('<li><a id="updateVersionItem-' + (i+3) + '">' + versions[i] + '</a></li>');

            if ($("#updateVersionsList").hasClass('ui-listview')) {
                 $("#updateVersionsList").listview("refresh");
            } else {
                 $("#updateVersionsList").trigger('create');
            }
        }

        $('[id^=updateVersionItem]').off("click").on("click", function(event, ui) {
            alert("updateVersion, selected = " + $(this).attr('id'));
        });
        /*$('#' + 'updateVersionItem-' + (i+3)).off("click").on("click", function(event, ui) {
            alert("updateVersion, selected = " + $(this).attr('id'));
        });*/
    });

    $('[id^=updateVersionItem]').on("click", function(event, ui) {
        alert("updateVersion, selected = " + $(this).attr('id'));
    });


    (function($) {
        /*
         * Changes the displayed text for a jquery mobile button.
         * Encapsulates the idiosyncrasies of how jquery re-arranges the DOM
         * to display a button for either an <a> link or <input type='button'>
         */
        $.fn.changeButtonText = function(newText) {
            return this.each(function() {
                $this = $(this);
                if( $this.is('a') ) {
                    $('span.ui-btn-text',$this).text(newText);
                    return;
                }
                if( $this.is('input') ) {
                    $this.val(newText);
                    // go up the tree
                    var ctx = $this.closest('.ui-btn');
                    $('span.ui-btn-text',ctx).text(newText);

                }
            });
        };
    })(jQuery);

});
