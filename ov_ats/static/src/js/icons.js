odoo.define('ov_ats.systray.Icons', function (require) {
"use strict";

    var core = require('web.core');
    var session = require('web.session');
    var SystrayMenu = require('web.SystrayMenu');
    var Widget = require('web.Widget');
    var QWeb = core.qweb;
    var rpc = require('web.rpc');
/**
 * Menu item appended in the systray part of the navbar, redirects to the next
 * activities of all app
 */
    var ActivityMenu2 = Widget.extend({
        name: 'activity_menu2',
        template:'ov_ats.systray.Icons',
        events: {
            'click .o_mail_preview': '_onSMSFilterClick',
            'click .o_show_sms': '_getSMSData',
        },
        init: function(parent, options) {
                var self = this;
                this._super.apply(this, arguments);
                return this._super();
            },
        start: function () {
            this._$activitiesPreview = this.$('.o_mail_systray_dropdown_items');
            this._updateSMSPreview();
            return this._super();
        },
        _getSMSData: function (data) {
            var self = this;
            rpc.query({
                model: 'pushbullet.sms.track',
                method: 'get_all_sms',
                args: [['id', 'message']],
            }).then(function (data) {
                console.log(data);
            });
        },

        /**
         * Update(render) activity system tray view on activity updation.
         * @private
         */
        _updateSMSPreview: function () {
            var self = this;
            // self._getSMSData().then(function (){
            //     //alert(data);
            //     self._$activitiesPreview.html(QWeb.render('ov_ats.systray.Icons.Previews', {
            //         smss : self._activities
            //     }));
            // });
        },

    });

    SystrayMenu.Items.push(ActivityMenu2);

    return ActivityMenu2;
    });