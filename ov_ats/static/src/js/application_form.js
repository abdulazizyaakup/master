// $(document).ready(function() {
//     $("#add").click(function() {
//             var lastField = $("#buildyourform div:last");
//         var intId = (lastField && lastField.length && lastField.data("idx") + 1) || 1;
//         var fieldWrapper = $("<div class=\"row fieldwrapper\" id=\"field" + intId + "\" style=\"line-height: 35px;width:100%;margin-left:0px;padding-top:10px;\"/>");
//         fieldWrapper.data("idx", intId);
//         var fName = $("<input type=\"text\" class=\"fieldname\" />");
//         var fType = $("<select class=\"fieldtype\"><option value=\"checkbox\">Checked</option><option value=\"textbox\">Text</option><option value=\"textarea\">Paragraph</option></select>");
//         var removeButton = $("<input type=\"button\" class=\"remove\" value=\"-\" />");
//         removeButton.click(function() {
//             $(this).parent().remove();
//         });
//         fieldWrapper.append(fName);
//         fieldWrapper.append(fType);
//         fieldWrapper.append(removeButton);
//         $("#buildyourform").append(fieldWrapper);
//     });
// });

$(document).ready(function() {
    $("#add").click(function() {
        var lastField = $("#buildyourform div:last");
        var intId = (lastField && lastField.length && lastField.data("idx") + 1) || 1;
        var fieldWrapper = $("<div class=\"row fieldwrapper\" id=\"field" + intId + "\" style=\"line-height: 35px;width:100%;margin-left:0px;padding-top:10px;\"/>");
        fieldWrapper.data("idx", intId);

        var Name = $("<div class=\"col-md-4 style=\"padding-left:15px;width:40%;\"><input type=\"text\" class=\"form-control o_website_form_input fieldname\" name=\"s_name\"/></div>");
        var HQA = $("<div class=\"col-md-4 style=\"padding-left:15px;width:40%;\"><input type=\"text\" class=\"form-control o_website_form_input fieldhqa\" name=\"s_hqa\"/></div>");
        var Year = $("<div class=\"col-md-2 style=\"padding-left:15px;width:10%;\"><input type=\"text\" class=\"form-control o_website_form_input fieldyear\" name=\"s_year\"/></div>");

        var removeButton = $("<div class=\"col-md-2 style=\"padding-left:15px;width:10%;\"><button class=\"fa btn btn-link fa-trash-o\"> Delete</button></div>");
        removeButton.click(function() {
            $(this).parent().remove();
        });
        fieldWrapper.append(Name);
        fieldWrapper.append(HQA);
        fieldWrapper.append(Year);
        fieldWrapper.append(removeButton);
        $("#buildyourform").append(fieldWrapper);
    });

});

$(document).ready(function() {
    $("#add2").click(function() {
        var lastField2 = $("#buildyourform2 div:last");
        var intId2 = (lastField2 && lastField2.length && lastField2.data("idx2") + 1) || 1;
        var fieldWrapper2 = $("<div class=\"row fieldwrapper2\" id=\"field2" + intId2 + "\" style=\"line-height: 35px;width:100%;margin-left:0px;\"/>");
        fieldWrapper2.data("idx2", intId2);
        var Language = $("<div class=\"col-md-4\" style=\"padding-left:15px;width:40%;\"><input type=\"text\" class=\"form-control o_website_form_input fieldlanguage\" name=\"l_name\"/></div>");
        var Spoken = $("<div class=\"col-md-3\" style=\"padding-left:15px;width:25%;\"><select id=\"proficiency_spoken\" class=\"form-control o_website_form_input\" style=\"width:100%%;\" name=\"l_proficiency_spoken\"><option t-attf-value=\"poor\" value=\"poor\">Poor</option><option t-attf-value=\"fair\" value=\"fair\">Fair</option><option t-attf-value=\"fluent\" value=\"fluent\">Fluent</option></select></div>");
        var Written = $("<div class=\"col-md-3\" style=\"padding-left:15px;width:25%;\"><select id=\"proficiency_spoken\" class=\"form-control o_website_form_input\" style=\"width:100%%;\" name=\"l_proficiency_written\"><option t-attf-value=\"poor\" value=\"poor\">Poor</option><option t-attf-value=\"fair\" value=\"fair\">Fair</option><option t-attf-value=\"good\" value=\"good\">Good</option></select></div>");

        var removeButton2 = $("<div class=\"col-md-2\" style=\"padding-left:15px;width:10%;\"><button class=\"fa btn btn-link fa-trash-o\"> Delete</button></div>");
        removeButton2.click(function() {
            $(this).parent().remove();
        });
        fieldWrapper2.append(Language);
        fieldWrapper2.append(Spoken);
        fieldWrapper2.append(Written);
        fieldWrapper2.append(removeButton2);
        $("#buildyourform2").append(fieldWrapper2);

        
    });

});


$(document).ready(function() {
    $("#add3").click(function() {
        var lastField3 = $("#buildyourform3 div:last");
        var intId3 = (lastField3 && lastField3.length && lastField3.data("idx3") + 1) || 1;
        var fieldWrapper3 = $("<div class=\"row fieldwrapper3\" id=\"field3" + intId3 + "\" style=\"line-height: 35px;width:100%;margin-left:0px;\"/>");
        fieldWrapper3.data("idx3", intId3);
        var Dialect = $("<div class=\"col-md-4\" style=\"padding-left:15px;width:50%;\"><input type=\"text\" class=\"form-control o_website_form_input fieldlanguage\" name=\"d_name\"/></div>");
        var Spoken = $("<div class=\"col-md-3\" style=\"padding-left:15px;width:25%;\"><select id=\"proficiency_dialect\" class=\"form-control o_website_form_input\" style=\"width:100%%;\" name=\"d_proficiency_dialect\"><option t-attf-value=\"poor\" value=\"poor\">Poor</option><option t-attf-value=\"fair\" value=\"fair\">Fair</option><option t-attf-value=\"fluent\" value=\"fluent\" >Fluent</option></select></div>");
        var Empty = $("<div class=\"col-md-3\" style=\"padding-left:15px;width:25%;\"></div>");
        var removeButton3 = $("<div class=\"col-md-2\" style=\"padding-left:15px;width:25%;\"><button class=\"fa btn btn-link fa-trash-o\"> Delete</button></div>");
        removeButton3.click(function() {
            $(this).parent().remove();
        });
        fieldWrapper3.append(Dialect);
        fieldWrapper3.append(Spoken);
        fieldWrapper3.append(Empty);
        fieldWrapper3.append(removeButton3);
        $("#buildyourform3").append(fieldWrapper3);

        
    });

});

$(document).ready(function() {
    $("#add4").click(function() {
        var lastField4 = $("#buildyourform4 div:last");
        var intId4 = (lastField4 && lastField4.length && lastField4.data("idx4") + 1) || 1;
        var fieldWrapper4 = $("<div class=\"row fieldwrapper4\" id=\"field4" + intId4 + "\" style=\"line-height: 45px;width:100%;margin-left:0px;\"/>");
        fieldWrapper4.data("idx4", intId4);
        var Date_From = $("<div class=\"col-md-2\" style=\"padding-left:15px;width:13%;\">From<div class=\"o_website_form_date input-group date\" id=\"datepicker3\" data-target-input=\"nearest\"><input type=\"text\" class=\"form-control datetimepicker-input o_website_form_input\" data-target=\"#datepicker3\" name=\"date_from\"/><div class=\"input-group-append\" data-target=\"#datepicker3\" data-toggle=\"datetimepicker\"><div class=\"input-group-text\"><i class=\"fa fa-calendar\"/></div></div></div></div>");
        var Date_To = $("<div class=\"col-md-2\" style=\"padding-left:15px;width:13%;\">To<div class=\"o_website_form_date input-group date\" id=\"datepicker4\" data-target-input=\"nearest\"><input type=\"text\" class=\"form-control datetimepicker-input o_website_form_input\" data-target=\"#datepicker4\" name=\"date_to\"/><div class=\"input-group-append\" data-target=\"#datepicker4\" data-toggle=\"datetimepicker\"><div class=\"input-group-text\"><i class=\"fa fa-calendar\"/></div></div></div></div>"
);
        var Company = $("<div class=\"col-md-2\" style=\"padding-left:15px;width:20%;\">Company<input type=\"text\" class=\"form-control o_website_form_input\" name=\"ch_name\"/></div>");
        var Position = $("<div class=\"col-md-2\" style=\"padding-left:15px;width:20%;\">Position<input type=\"text\" class=\"form-control o_website_form_input\" name=\"ch_position_held\"/></div>");
        var GS = $("<div class=\"col-md-1\" style=\"padding-left:15px;width:10%;\">Salary<input type=\"text\" class=\"form-control o_website_form_input\" name=\"ch_gross_sal\"/></div>");
        var RL = $("<div class=\"col-md-2\" style=\"padding-left:15px;width:20%;\">Reason Leave<textarea type=\"text\" class=\"form-control o_website_form_input\" name=\"ch_reason_leave\"/></div>");
        var removeButton4 = $("<div class=\"col-md-1\" style=\"padding-left:15px;width:4%;\"><button class=\"fa btn btn-link fa-trash-o\"> Delete</button></div>");
        removeButton4.click(function() {
            $(this).parent().remove();
        });
        fieldWrapper4.append(Date_From);
        fieldWrapper4.append(Date_To);
        fieldWrapper4.append(Company);
        fieldWrapper4.append(Position);
        fieldWrapper4.append(GS);
        fieldWrapper4.append(RL);
        fieldWrapper4.append(removeButton4);
        $("#buildyourform4").append(fieldWrapper4);

        
    });

});


$(document).ready(function() {
    $("#add5").click(function() {
        var lastField5 = $("#buildyourform5 div:last");
        var intId5 = (lastField5 && lastField5.length && lastField5.data("idx5") + 1) || 1;
        var fieldWrapper5 = $("<div class=\"fieldwrapper5 row\" id=\"field5" + intId5 + "\" style=\"padding-left:15px;line-height: 35px;width:100%;margin-left:0px;\"/>");
        fieldWrapper5.data("idx5", intId5);
        var Name = $("<div class=\"col-md-4\"><input type=\"text\" class=\"form-control o_website_form_input fieldname\" name=\"r_name\"/></div>");
        var Relationship = $("<div class=\"col-md-4\"><input type=\"text\" class=\"form-control o_website_form_input fieldrelationship\" name=\"r_relationship\"/></div>");
        

        var removeButton5 = $("<div class=\"col-md-4\"><button class=\"fa btn btn-link fa-trash-o\"> Delete</button></div>");
        removeButton5.click(function() {
            $(this).parent().remove();
        });
        fieldWrapper5.append(Name);
        fieldWrapper5.append(Relationship);
        fieldWrapper5.append(removeButton5);
        $("#buildyourform5").append(fieldWrapper5);

        
    });

});

// $(document).ready(function() {
//     $("#gothere").click(function() {
//         alert("Test")
//     });

// });
// $(document).ready(function() {
//     $("#add6").click(function() {
//         var lastField6 = $("#buildyourform6 div:last");
//         var intId6 = (lastField6 && lastField6.length && lastField6.data("idx") + 1) || 1;
//         var fieldWrapper6 = $("<div class=\"fieldwrapper6\" id=\"field" + intId6 + "\"/>");
//         fieldWrapper6.data("idx", intId6);
//         var fName = $("<input type=\"text\" class=\"fieldname\" />");
//         var fType = $("<select class=\"fieldtype\"><option value=\"checkbox\">Checked</option><option value=\"textbox\">Text</option><option value=\"textarea\">Paragraph</option></select>");
//         var removeButton6 = $("<input type=\"button\" class=\"remove\" value=\"-\" />");
//         removeButton6.click(function() {
//             $(this).parent().remove();
//         });
//         fieldWrapper6.append(fName);
//         fieldWrapper6.append(fType);
//         fieldWrapper6.append(removeButton6);
//         $("#buildyourform6").append(fieldWrapper6);
//     });
// });
