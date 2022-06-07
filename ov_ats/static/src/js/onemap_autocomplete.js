odoo.define('ov_ats.onemap_autocomplete', function (require) {
    'use strict';
    var Widget = require('web.Widget');
    // var widgetRegistry = require('web.widget_registry');
    // var core = require('web.core');
    var BasicFields = require('web.basic_fields');
    var core = require('web.core');
    // var Utils = require('web_google_maps.Utils');
    var _t = core._t;

    var bh_sidebar = Widget.extend({
        init: function () {
            var self = this;
            this._super(parent);
            console.log('Widget initialized!');
        },
        supportedFieldTypes: ['char'],
        events: _.extend({}, BasicFields.InputField.prototype.events, {
            'focus': '_test',
        }),

        start: function () {
            //this.$el.append(QWeb.render('bh_sidebar_template'));
            console.log('Widget started!');
            this.$el.append("<div>Hello dear Odoo user!</div>");
        },
        _test: function () {
            // console.log('HAHAHAAHA');
        },
    });

    var registry = require('web.field_registry');
    registry.add('bh_sidebar', bh_sidebar);
})