odoo.define('ov_hr_recruitment_ext.copy_url', function (require) {
"use strict";

var rpc = require('web.rpc')

rpc.query{(
    model: 'hr.applicant';//your model,
    method: 'copy_link';//your method,
        args: [{
            'arg1': value1,
        }]

 ).then(function (result) { 

            alert ("Test");

            });
};
});