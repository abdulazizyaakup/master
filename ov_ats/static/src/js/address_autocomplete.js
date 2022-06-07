odoo.define('ov_ats.address_autocomplete', function (require) {
    'use strict';

    require('web.dom_ready');
    var ajax = require('web.ajax');
    var core = require('web.core');

    var _t = core._t;

    var lastsearch;

    $('input.js_select3').select2({
        text: true,
        maximumInputLength: 35,
        maximumSelectionSize: 1,
        lastsearch: [],
        createSearchChoice: function (term) {
            if ($(lastsearch).filter(function () { return this.text.localeCompare(term) === 0;}).length === 0) {
                //check Karma
                if (parseInt($("#karma").val()) >= parseInt($("#karma_edit_retag").val())) {
                    return {
                        id: "_" + $.trim(term),
                        text: $.trim(term) + ' *',
                        isNew: true,
                    };
                }
            }
        },
        formatResult: function(term) {
            return _.escape(term.text);
        },
        ajax: {
            url: '/ats/address',
            dataType: 'json',
            data: function(term) {
                return {
                    q: term,
                    l: 100
                };
            },
            results: function(data) {
                var ret = [];
                _.each(data, function(x) {
                    ret.push({ id: x.ADDRESS,text: x.ADDRESS});
                });
                lastsearch = ret;
                return { results: ret };
            }
        },
        // Take default tags from the input value
        //formatSelection: formatSelection,
        initSelection: function (element, callback) {
            var data;
            _.each(element.data('init-value'), function(x) {
                data.push({id: x.ADDRESS, text: x.ADDRESS});
            });
            element.val('');
            callback(data);
        },
    });

    // $(document).ready(function () {
    //     // disabled submit form when user press 'enter' key
    //     $('.o_portal_wrap').find('form').on('keypress', function (ev) {
    //         var key_code = ev.keyCode || ev.which;
    //         if (key_code === 13) {
    //             ev.preventDefault();
    //             return false;
    //         }
    //     });
    // });

});