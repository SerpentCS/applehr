odoo.define('appointment_booking_contact_us.start', function (require) {

    $(document).ready(function myFunction() {

        $('#datetimepickerID').datetimepicker({ format: 'YYYY-MM-DD HH:mm:ss' , inline: true,
        sideBySide: true, daysOfWeekDisabled: [0, 6] });
    })

    var publicWidget = require('web.public.widget');
    const ajax = require('web.ajax');

    publicWidget.registry.appointmentForm.include({
        start: function () {
            return this._super(...arguments).then(async () => {
                $(".appointment_submit_form .btn").click();
            });
        },
    })

    publicWidget.registry.customRedirectButton = publicWidget.Widget.extend({
        selector: '#custom_redirect_button',
        events: {
            'click': '_onClickRedirectButton',
        },
        _onClickRedirectButton: async function (ev) {
            ev.preventDefault();
            var appointment_type_id = $(ev.currentTarget).data('appointment_type_id')
            var formData = this._getFormData();
            const serializedData = encodeURIComponent(JSON.stringify(formData));
            const appointmentPageURL = `/appointment/${appointment_type_id}?data=${serializedData}`;
            window.location.href = appointmentPageURL;
        },
        _getFormData: function () {
            var formData = {};
            this.$el.closest('form').serializeArray().forEach(function (field) {
                formData[field.name] = field.value;
            });
            return formData;
        },
    });
    return publicWidget.registry.customRedirectButton;
});