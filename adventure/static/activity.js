/*
* Adventure664 - A django-based adventure game
* Written as a demo for UMSI 664 
* 
* Copyright (C) 2020-2022 Edward L. Platt <ed@elplatt.com> 
* Distributed under the GNU AGPL 3.0 <https://www.gnu.org/licenses/agpl-3.0.en.html>
*
* This file provides an enableAjax() function to automatically update the activity list in
* area detail views.
*/

Activity = {

	// Timeout in ms
	timeout: 1000,
	areaId: 0,

	// Get the url for area
	getUrl: function (areaId) { return `/api/explore/${areaId}/activity`; },

    // Begin polling activity for `areaId`
	enableAjax: function (areaId) {
		Activity.areaId = areaId;
		window.setTimeout(Activity.poll, Activity.timeout, areaId);
	},

	// Poll activity
	poll: function (areaId) {
		let url = Activity.getUrl(areaId);
		let request = new XMLHttpRequest();
		request.open("GET", url);
		request.addEventListener("load", Activity.onLoad);
		request.send();
	},

	// Handle response from activity poll
	onLoad: function () {
		let data = JSON.parse(this.responseText);
		console.log(data);
		Activity.enableAjax(Activity.areaId);
	}
};
