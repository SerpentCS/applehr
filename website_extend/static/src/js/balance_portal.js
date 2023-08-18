/** @odoo-module */

import publicWidget from 'web.public.widget';

function initializeDatepickers() {
    $(".datepicker").datepicker({
        dateFormat: 'mm-dd-yy',
    });
}

$(document).ready(function () {
    initializeDatepickers();

    // $('#submit-button').click(function () {
    //     handleFormSubmission();
    //     return false;
    // });

    publicWidget.registry.PortalHomeCounters.include({
        /**
         * @override
         */
        _getCountersAlwaysDisplayed() {
            return this._super(...arguments).concat(['balance_count', 'balance_record']);
        },
    });
});

// function handleFormSubmission() {

//     var start_date = $('#start_date').val();
//     var end_date = $('#end_date').val();


//     if (start_date === "" || end_date === "") {
//         // Display validation message in the div
//         $('#validation_message').html("Both Start Date and End Date are required.");
//         $('#print-button').hide(); // Hide the button
//         return false;
//     } else {
//         $('#validation_message').empty(); // Clear previous validation message
//         $('#print-button').show(); // Show the button
//         $('#data_table').show(); // Show the button



//         console.log("START_DATE", start_date);
//         console.log("END_DATE", end_date);

//         var data_values = {
//             start_date: start_date,
//             end_date: end_date,
//         };

//         $.ajax({
//             url: '/my/quotes/history/',  // Specify the URL to send the data to
//             method: 'POST',   
//             data: data_values,
//         });

//     }
// }
