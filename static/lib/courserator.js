var CURRENT_DATA = null;

var currentSource = null;
function calendarShowSchedule(sections, schedule) {
	var calendar = $("#calendar");
	
	if (currentSource !== null) calendar.fullCalendar("removeEventSource", currentSource);
	currentSource = { events: function(start, end, timezone, callback) { return callback(calendarGetEvents(sections, schedule, moment(start), moment(end))); } };
	calendar.fullCalendar("addEventSource", currentSource);
	
	calendarGoToEarliest(sections, schedule);
}

function calendarGoToEarliest(sections, schedule) { // to the the first day of the given schedule
	// go to first day in schedule
	console.log(schedule);
	console.log(sections);
	var earliest = moment(sections[schedule[0]].blocks[0][0]);
	for (var i = 0; i < schedule.length; i ++) { // add new events
		var blocks = sections[schedule[i]].blocks;
		for (var j = 0; j < blocks.length; j ++) {
			var block = blocks[j];
			if (earliest.isAfter(block[0])) earliest = moment(block[0]);
		}
	}
	$("#calendar").fullCalendar("gotoDate", earliest);
}

function calendarGetEvents(sections, schedule, start, end) { // obtain the events in the given schedule in the given interval
	var events = [];
	for (var i = 0; i < schedule.length; i ++) { // add new events
		var section = sections[schedule[i]];
		for (var j = 0; j < section.blocks.length; j ++) {
			var block = section.blocks[j];
			var blockStart = moment.utc(block[0]); blockEnd = moment.utc(block[1]); // parse times without time zone offsets
			if (start.isBefore(block[1]) && end.isAfter(block[0])) {
				events.push({
					title: section.name + " " + section.section,
					start: block[0], end: block[1], allDay: false,
					className: "classBlock",
				});
			}
		}
	}
	return events;
}

function tableShowScheduleList(scheduleStats) {
	var table = $("#scheduleList");
	table.DataTable().destroy(); // destroy the old schedule list
	table.DataTable({
		data: scheduleStats,
		columns: [
			{ data: "earliest", width: "auto" },
			{ data: "latest", width: "auto" },
			{ data: "instructors", width: "auto" },
		],
		paging: false,
		scrollY: 400,
	});
}

function queryValidateCourses() {
	var query = $("#query");
	var courseList = query.val().split(",");
	var isValid = /^(\s*[a-zA-Z]+\s*\d\w*\s*)(,\s*[a-zA-Z]+\s*\d\w*\s*)*$/.test(courseList);
	query[0].setCustomValidity("");
	query[0].setCustomValidity(isValid ? "" : "Enter a comma-separated list of courses");
	return isValid;
}

function querySearchCourses(event) {
	event.preventDefault(); //stop submit
	if (!queryValidateCourses()) return;
	
	var term = $("#term").val();
	var resultURL = "schedules/" + term + "/" + $("#query").val(); // wip: term selection
	$("#progress").show();
	$.get(resultURL, function(data) {
		$("#progress").hide();
		console.log(data);
		CURRENT_DATA = data;
		tableShowScheduleList(data.schedule_stats);
		
		$("#scheduleList").find("tr:nth-child(1)").addClass("selected"); // select the second row (first row is headers)
		calendarShowSchedule(CURRENT_DATA.sections, CURRENT_DATA.schedules[0]); // show the first schedule
	}, "json");
}

$(document).ready(function() {
	$("#courses").submit(querySearchCourses);
	$("#query").on("input", queryValidateCourses);
	queryValidateCourses();
	
	var table = $("#scheduleList");
	table.find("tbody").on("click", "tr", function () {
		table.find("tr.selected").removeClass("selected"); // deselect all other rows
		$(this).addClass("selected"); // select this row
		calendarShowSchedule(CURRENT_DATA.sections, CURRENT_DATA.schedules[table.DataTable().row(".selected").index()]);
	});
	
	tableShowScheduleList([]);
	
	// set up the calendar
	$("#calendar").fullCalendar({
		defaultView: "agendaWeek", // start with a weekly agenda
		firstDay: 1, // weeks start on Monday
		height: "auto",
		businessHours: { // emphasize business hours
			start: "8:00", end: "22:00",
			dow: [1, 2, 3, 4, 5], // business days
		},
		minTime: "8:00", maxTime: "22:00",
		allDaySlot: false,
	});
});
