odoo.define('ov_tender.website_sale', function (require) {
    'use strict';

    require('web.dom_ready');
    var ajax = require('web.ajax');
    var core = require('web.core');

    var _t = core._t;

    var lastsearch;


    $('input.js_select2').select2({
        tags: true,
        tokenSeparators: [",", " ", "_"],
        maximumInputLength: 35,
        maximumSelectionSize: 10,
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
            if (term.isNew) {
                return '<span class="badge badge-primary">New</span> ' + _.escape(term.text);
            }
            else {
                return _.escape(term.text);
            }
        },
        ajax: {
            url: '/tenderquote/get_keywords',
            dataType: 'json',
            data: function(term) {
                return {
                    q: term,
                    l: 50
                };
            },
            results: function(data) {
                var ret = [];
                _.each(data, function(x) {
                    ret.push({ id: x.id, text: x.name, isNew: false });
                });
                lastsearch = ret;
                return { results: ret };
            }
        },
        // Take default tags from the input value
        initSelection: function (element, callback) {
            var data = [];
            _.each(element.data('init-value'), function(x) {
                data.push({ id: x.id, text: x.name, isNew: false });
            });
            element.val('');
            callback(data);
        },
    });

});