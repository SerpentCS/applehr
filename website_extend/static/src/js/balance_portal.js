/** @odoo-module */

import publicWidget from 'web.public.widget';

function initializeDatepickers() {
    $(".datepicker").datepicker({
        dateFormat: 'dd-mm-yy',
    });
}

$(document).ready(function () {
    initializeDatepickers();

    publicWidget.registry.PortalHomeCounters.include({
        /**
         * @override
         */
        _getCountersAlwaysDisplayed() {
            return this._super(...arguments).concat(['balance_count', 'balance_record']);
        },
    });
});