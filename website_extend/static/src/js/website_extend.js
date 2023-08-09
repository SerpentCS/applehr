

function validateForm() {
    const requiredFields = document.querySelectorAll('input[required]');
    let isValid = true;
    requiredFields.forEach(function (field) {
        if (field.value.trim() === '') {
            isValid = false;
        }
    });
    if (!isValid) {
        const errorElement = document.getElementById('error-message');
        errorElement.textContent = ' *Please fill in all the required fields.';
    }
    return isValid;
}

odoo.define('website_extend.website_extend', function (require) {
    "use strict";

    const ajax = require('web.ajax');
    var publicWidget = require('web.public.widget');

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

            if (validateForm()) {
                ev.preventDefault();
                var appointment_type_id = $(ev.currentTarget).data('appointment_type_id')
                var formData = this._getFormData();
                const serializedData = encodeURIComponent(JSON.stringify(formData));
                const appointmentPageURL = `/appointment/${appointment_type_id}?data=${serializedData}`;
                window.location.href = appointmentPageURL;
            }
        },
        _getFormData: function () {
            var formData = {};
            this.$el.closest('form').serializeArray().forEach(function (field) {
                formData[field.name] = field.value;
            });
            return formData;
        },
    });

});