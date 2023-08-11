odoo.define('website_extend.fullscreen', function (require) {
    "use strict";

    var core = require('web.core');
    var Fullscreen = require('@website_slides/js/slides_course_fullscreen_player')[Symbol.for("default")];

    var findSlide = function (slideList, matcher) {
        var slideMatch = _.matcher(matcher);
        return _.find(slideList, slideMatch);
    };


    Fullscreen.include({
        init: function (parent, slides, defaultSlideId, channelData) {
            var result = this._super.apply(this, arguments);
            this.sidebar._onClickTab = this._onClickTab;
            this.sidebar.events['click .o_wslides_fs_slide_link'] = this._onClickAdditionalResources;
            document.addEventListener("contextmenu", (event) => {
                event.preventDefault();
            });
            return result;
        },
        _onClickTab: function (ev) {
            ev.stopPropagation();
            $(".parent_slide").show();
            $("#additional_resources_iframe").addClass('d-none');
            const $elem = $(ev.currentTarget).closest('.o_wslides_fs_sidebar_list_item');
            if ($elem.data('canAccess') === 'True') {
                var isQuiz = $elem.data('isQuiz');
                var slideID = parseInt($elem.data('id'));
                var slide = findSlide(this.slideEntries, { id: slideID, isQuiz: isQuiz });
                this.set('slideEntry', slide);
            }
        },
        _onClickAdditionalResources: function (ev) {
            ev.stopPropagation();
            var additional_url = $(ev.currentTarget).data('additional_url');
            $("#additional_resources_iframe").attr({ 'src': additional_url });
            $("#additional_resources_iframe").removeClass('d-none');
            $(".parent_slide").hide();
        }
    });

});

