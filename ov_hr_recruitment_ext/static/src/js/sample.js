odoo.define('ov_hr_recruitment_ext.sample', function (require) {
    "use strict";

    var core = require('web.core');
    var ListView = require('web.ListView');
    var QWeb = core.qweb;

    var _t = core._t;

    ListView.include({
        redraw: function () {
            var self = this;
        }, // <<<<< You missed this


        events: {
            "click .export_treeview_xls": "your_function",
        },

        your_function: function () {
            alert('Button Clicked');
        },

    });
});

