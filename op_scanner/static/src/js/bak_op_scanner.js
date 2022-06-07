odoo.define('op_scanner.op_scanner', function(require){
    "use strict";

    var core = require('web.core');
    var Widget = require('web.Widget');
    var ControlPanelMixin = require('web.ControlPanelMixin');
    var AbstractAction = require('web.AbstractAction');
    var rpc = require('web.rpc');
    var ajax = require('web.ajax');
    var qweb = core.qweb;
    require('web.dom_ready');
    require('web.core').csrf_token
    var session = require('web.session');

    var Dialog = require('web.Dialog');
    var field_utils = require('web.field_utils');
    var web_client = require('web.web_client');

    var _t = core._t;
    var url = window.location.href;


    Dynamsoft.WebTwainEnv.Containers = [{ContainerId:'dwtcontrolContainer', Width:370, Height:415}];

    var TwainContainer = AbstractAction.extend(ControlPanelMixin, {
        template: 'TwainContainer',
        // fetchInject([
        //     '/op_scanner/static/lib/Dynamsoft/dynamsoft.webtwain.config.js',
        // ]),
        cssLibs: [
        '/op_scanner/static/src/css/op_scanner.css',
        '/op_scanner/static/src/css/prettify.css',
        '/op_scanner/static/src/css/style.css',
        ],
        jsLibs: ['/op_scanner/static/src/js/dynamsoft.webtwain.config.js',
                 '/op_scanner/static/src/js/dynamsoft.webtwain.initiate.js',
                ],
        events: {
            'click .o_acquire_image': '_AcquireImage',
            'click .o_duplex_option': '_DuplexScan',
            'click .o_download_file': '_DownloadImage',
            'change .o_preview_mode': '_setlPreviewMode',
            'click .o_save_file': '_SaveWithFileDialog',
            'click .o_save_model': '_SaveToFolder',
            'click .o_upload_file': '_LoadImage',
        },
        init: function(parent, options) {
            var self = this;
            this._super.apply(this, arguments);
            this.options = _.extend(options || {}, {
                csrf_token: odoo.csrf_token,
            });
            $.getScript("/op_scanner/static/src/js/dynamsoft.webtwain.initiate.js", function(){
                   console.log("Script loaded but not necessarily executed.");
            });
            //return $.when(this._super(), ajax.loadXML('/op_scanner/static/src/xml/op_scanner.xml', qweb));
        },
        start: function() {
            var self = this;
            Dynamsoft.WebTwainEnv.RegisterEvent('OnWebTwainReady', self._Dynamsoft_OnReady);
            self._Dynamsoft_OnReady();
            //var location = document.location.href;
            var location = window.location.pathname;

            console.log("LOCATIONS      :"+location);
            // console.log("URL DEFAULT "+ default_url);
            // var str = window.location.href;
            // var current_url = str.replace("#", "?");
            // var url = new URL(current_url);
            // var res_id = url.searchParams.get("id");
            // var res_model = url.searchParams.get("model");
            // return $.when(this._super(), ajax.loadXML('/op_scanner/static/src/xml/op_scanner.xml', qweb));
            return self._super();
        },
        willStart: function () {
            return this._super();
        },
        _Dynamsoft_OnReady: function() {
            var self = this;
            var DWObject;
            // DWObject = Dynamsoft.WebTwainEnv.GetWebTwain('dwtcontrolContainer');
            // if (DWObject) {
            //     DWObjectLargeViewer = Dynamsoft.WebTwainEnv.GetWebTwain('dwtcontrolContainerLargeViewer'); // Get the 2nd Dynamic Web TWAIN object that is embeded in the div with id 'dwtcontrolContainerLargeViewer'

            //     DWObjectLargeViewer.SetViewMode(-1, -1); // When the view mode is set to -1 by -1, the control only shows the current image. No scroll bar is provided to navigate to other images.
            //     DWObjectLargeViewer.MaxImagesInBuffer = 1; // Set it to hold one image only
            //     DWObject.SetViewMode(1, 3); // Set the view mode to 1 by 3. In this view mode, when the number of the images in the buffer is larger than 3 (1 x 3), a scroll bar is provide to navigate to other images.
                
            //     var count = DWObject.SourceCount; // Get how many sources are installed in the system
                
            //     for (var i = 0; i < count; i++)
            //         document.getElementById("source").options.add(new Option(DWObject.GetSourceNameItems(i), i)); // Add the sources in a drop-down list

            //     // Register the events
            //     DWObject.RegisterEvent("OnPostTransfer", self._Dynamsoft_OnPostTransfer);
            //     DWObject.RegisterEvent("OnPostLoad", self._Dynamsoft_OnPostLoad);
            //     DWObject.RegisterEvent("OnMouseClick", self._Dynamsoft_OnMouseClick);
            // }

            DWObject = Dynamsoft.WebTwainEnv.GetWebTwain('dwtcontrolContainer'); // Get the Dynamic Web TWAIN object that is embeded in the div with id 'dwtcontrolContainer'
            if (DWObject) {
                var count = DWObject.SourceCount;
                for (var i = 0; i < count; i++)
                    document.getElementById("source").options.add(new Option(DWObject.GetSourceNameItems(i), i));

            }
        },
        _AcquireImage: function() {
            //var self = this;
            var DWObject = Dynamsoft.WebTwainEnv.GetWebTwain('dwtcontrolContainer');
            if (DWObject) {
                var OnAcquireImageSuccess, OnAcquireImageFailure;
                OnAcquireImageSuccess = OnAcquireImageFailure = function () {
                    DWObject.CloseSource();
                };

                DWObject.SelectSourceByIndex(document.getElementById("source").selectedIndex);
                DWObject.OpenSource();
                DWObject.IfDisableSourceAfterAcquire = true;
                //Pixel type
                if (document.getElementById("BW").checked)
                    DWObject.PixelType = EnumDWT_PixelType.TWPT_BW;
                else if (document.getElementById("Gray").checked)
                    DWObject.PixelType = EnumDWT_PixelType.TWPT_GRAY;
                else if (document.getElementById("RGB").checked)
                    DWObject.PixelType = EnumDWT_PixelType.TWPT_RGB;
                //If auto feeder
                if (document.getElementById("ADF").checked)
                    DWObject.IfFeederEnabled = true;
                else
                    DWObject.IfFeederEnabled = false;
                //If show UI
                if (document.getElementById("ShowUI").checked)
                    DWObject.IfShowUI = true;
                else
                    DWObject.IfShowUI = false;
                //Resolution
                DWObject.Resolution = parseInt(document.getElementById("Resolution").value);

                if (document.getElementById("ADF").checked && DWObject.IfFeederEnabled == true)  // if paper is NOT loaded on the feeder
                {
                    if (DWObject.IfFeederLoaded != true && DWObject.ErrorCode == 0) {
                        alert("No paper detected! Please load papers and try again!");
                        return;
                    }
                }

                DWObject.AcquireImage(OnAcquireImageSuccess, OnAcquireImageFailure);
            }
        },

        _SaveToFolder: function(){
            var DWObject = Dynamsoft.WebTwainEnv.GetWebTwain('dwtcontrolContainer');
            var strHTTPServer = location.hostname; //The name of the HTTP server. For example: "www.dynamsoft.com";
            var CurrentPathName = unescape(location.pathname);
            var CurrentPath = CurrentPathName.substring(0, CurrentPathName.lastIndexOf("/") + 1);
            var strActionPage = CurrentPath + "SaveToFile.aspx";
            DWObject.IfSSL = false; // Set whether SSL is used
            DWObject.HTTPPort = location.port == "" ? 80 : location.port;

            // var hahaha = chrome.downloads.DownloadItem.filename;
            // console.log("HAHAHAHAHA : "+hahaha);
            // chrome.downloads.showDefaultFolder()
            const xhr = new XMLHttpRequest();
            xhr.onload = () => {
                if (xhr.status >= 200 && xhr.status < 300) {
                    // we done!
                }
            };


            var canvas = document.querySelector("#dwtcontrolContainer canvas");
            var dataURL = canvas.toDataURL("image/png");
            var default_url = window.location.href;
            var current_url = default_url.replace("#", "?");
            var new_url = new URL(current_url);
            var res_id = new_url.searchParams.get("active_id");
            var res_model = new_url.searchParams.get("model");
            var user = session.uid;
            var title = document.getElementById('txt_title').value;
            var name = document.getElementById('txt_fileName').value;
            var description = document.getElementById('txt_description').value;
            var fileType = document.getElementById('fileType').value;
            
            //var locations = unescape("/home/aziz/");
            var locations2 = unescape("/home/aziz/");
            var locations = unescape("C:\\Users\\Public\\");
            var filename = name+"-"+user;
            var doc_name;

            console.log("URL DEFAULT :"+default_url);
            console.log("URL DEFAULT :"+current_url);
            console.log("URL DEFAULT :"+new_url);
            console.log("ID :"+res_id);
            console.log("MODEL :"+res_model);

            
            DWObject.IfShowFileDialog = false;
            if (document.getElementById("imgTypejpeg").checked == true) {
                //If the current image is B&W
                //1 is B&W, 8 is Gray, 24 is RGB
                if (DWObject.GetImageBitDepth(DWObject.CurrentImageIndexInBuffer) == 1){
                    //If so, convert the image to Gray
                    DWObject.ConvertToGrayScale(DWObject.CurrentImageIndexInBuffer);
                //Save image in JPEG
                }
                DWObject.SaveAsJPEG(locations+filename+".jpg", DWObject.CurrentImageIndexInBuffer);
                doc_name = filename+".jpg";
            }
            else if (document.getElementById("imgTypepng").checked == true) {
                //If the current image is B&W
                //1 is B&W, 8 is Gray, 24 is RGB
                if (DWObject.GetImageBitDepth(DWObject.CurrentImageIndexInBuffer) == 1){
                    //If so, convert the image to Gray
                    DWObject.ConvertToGrayScale(DWObject.CurrentImageIndexInBuffer);
                //Save image in JPEG
                }
                DWObject.SaveAsPNG(locations+filename+".png", DWObject.CurrentImageIndexInBuffer);
                doc_name = filename+".png";
            }
            else if (document.getElementById("imgTypebmp").checked == true) {
                //If the current image is B&W
                //1 is B&W, 8 is Gray, 24 is RGB
                if (DWObject.GetImageBitDepth(DWObject.CurrentImageIndexInBuffer) == 1){
                    //If so, convert the image to Gray
                    DWObject.ConvertToGrayScale(DWObject.CurrentImageIndexInBuffer);
                //Save image in JPEG
                }
                DWObject.SaveAsBMP(locations+filename+".bmp", DWObject.CurrentImageIndexInBuffer);
                doc_name = filename+".bmp";
            }
            else if (document.getElementById("imgTypetiff").checked == true){
                DWObject.SaveAllAsMultiPageTIFF(locations+filename+".tiff", this._OnSuccess, this._OnFailure);
                doc_name = filename+".tiff";
            }
            else if (document.getElementById("imgTypepdf").checked == true){
                DWObject.SaveAllAsPDF(locations+filename+".pdf", this._OnSuccess, this._OnFailure);
                doc_name = filename+".pdf";
            }
            // alert("Save Completed");
            // ajax.jsonRpc('/attachment/save/','call',{'name': name,'doc_name': doc_name, 'applicant_id':res_id, 'res_model':res_model}).then(function(data){
            //     console.log("SUCCESS");
            // });
            // var test = ajax.jsonRpc('/attachment/save/','call',{'title':title,'name': name,'description':description,'doc_name': doc_name, 'applicant_id':res_id, 'res_model':res_model,'fileType':fileType}).then(function(data){
            //     console.log("Success");
            // });
            // setTimeout(function(){ 
            //     alert("Documents Successfuly Saved");
            //     window.location = url;
            //     return test;//this._SaveToModel(default_url,title,name,description,doc_name,res_id,res_model,fileType);
            // }, 5000);
            //alert("Documents Successfuly Saved");
            //return window.location = url;
            
        },
        _SaveToModel: function(default_url,title,name,description,doc_name,res_id,res_model,fileType){
            ajax.jsonRpc('/attachment/save/','call',{'title':title,'name': name,'description':description,'doc_name': doc_name, 'applicant_id':res_id, 'res_model':res_model,'fileType':fileType}).then(function(data){
                console.log("success");
                setTimeout(function(){ 
                    
                    //this.do_notify(_t("Success"), _t("Document have been saved."));
                    alert("Documents Successfuly Saved");
                     }, 3000);
                return window.location = default_url;

            });
        },
        _Dynamsoft_OnPostTransfer: function() { // The event OnPostTransfer will get fired after a transfer ends.
            this._updateLargeViewer();
        },
        _Dynamsoft_OnPostLoad: function(path, name, type) { // The event OnPostLoad will get fired after the images from a local directory have been loaded into the control.
            this._updateLargeViewer();
        },
        _Dynamsoft_OnMouseClick: function() { // The event OnMouseClick will get fired when the mouse clicks on an image.
            this._updateLargeViewer();
        },
        _updateLargeViewer: function() {
            DWObject.CopyToClipboard(DWObject.CurrentImageIndexInBuffer); // Copy the current image in the thumbnail to clipboard in DIB format.
            DWObjectLargeViewer.LoadDibFromClipboard(); // Load the image from Clipboard into the large viewer.
        },
        _DuplexScan: function(){
            var DWObject = Dynamsoft.WebTwainEnv.GetWebTwain('dwtcontrolContainer');
            DWObject.SelectSource();
            DWObject.OpenSource();
            if (DWObject.Duplex != 0)        
                DWObject.IfDuplexEnabled = true ;//Enable duplex 

            DWObject.XferCount = 2;
            DWObject.MaxImagesInBuffer = 2;
            DWObject.AcquireImage();
        },
        _OnSuccess: function () {
            console.log('successful');
        },
        _OnFailure: function(errorCode, errorString) {
            alert(errorString);
        },
        _RotateLeft: function () {
            var DWObject = Dynamsoft.WebTwainEnv.GetWebTwain('dwtcontrolContainer');
            if (DWObject)
                if (DWObject.HowManyImagesInBuffer > 0)
                    DWObject.RotateLeft(DWObject.CurrentImageIndexInBuffer);
        },
        _RotateRight: function () {
            var DWObject = Dynamsoft.WebTwainEnv.GetWebTwain('dwtcontrolContainer');
            if (DWObject)
                if (DWObject.HowManyImagesInBuffer > 0)
                    DWObject.RotateRight(DWObject.CurrentImageIndexInBuffer);
        },
        _Mirror: function () {
            var DWObject = Dynamsoft.WebTwainEnv.GetWebTwain('dwtcontrolContainer');
            if (DWObject)
                if (DWObject.HowManyImagesInBuffer > 0)
                    DWObject.Mirror(DWObject.CurrentImageIndexInBuffer);
        },
        _Flip: function () {
            var DWObject = Dynamsoft.WebTwainEnv.GetWebTwain('dwtcontrolContainer');
            if (DWObject)
                if (DWObject.HowManyImagesInBuffer > 0)
                    DWObject.Flip(DWObject.CurrentImageIndexInBuffer);

        },
        _DownloadImage: function () {
            var DWObject = Dynamsoft.WebTwainEnv.GetWebTwain('dwtcontrolContainer');
            if (DWObject) {
                var strHTTPServer = location.hostname; //The name of the HTTP server. For example: "www.dynamsoft.com";
                var file = document.getElementsByTagName("canvas").src;//"/UploadedImages/img.png";
                console.log("URL :" + file);
                // var downloadfilename = location.pathname.substring(0, location.pathname.lastIndexOf('/')) + file;
                // DWObject.HTTPPort = location.port == "" ? 80 : location.port;
                // DWObject.HTTPDownload(strHTTPServer, downloadfilename, this._OnSuccess, this._OnFailure);
            }
        },
        _setlPreviewMode: function () {
            var DWObject = Dynamsoft.WebTwainEnv.GetWebTwain('dwtcontrolContainer');
            if (DWObject) {
                var o = parseInt(document.getElementById("DW_PreviewMode").selectedIndex + 1);
                DWObject.SetViewMode(o, o);
            }
        },
        _SaveWithFileDialog: function () {
            var DWObject = Dynamsoft.WebTwainEnv.GetWebTwain('dwtcontrolContainer');
            if (DWObject) {
                if (DWObject.HowManyImagesInBuffer > 0) {
                    DWObject.IfShowFileDialog = true;
                    if (document.getElementById("imgTypejpeg").checked == true) {
                        //If the current image is B&W
                        //1 is B&W, 8 is Gray, 24 is RGB
                        if (DWObject.GetImageBitDepth(DWObject.CurrentImageIndexInBuffer) == 1)
                            //If so, convert the image to Gray
                            DWObject.ConvertToGrayScale(DWObject.CurrentImageIndexInBuffer);
                        //Save image in JPEG
                        DWObject.SaveAsJPEG("DynamicWebTWAIN.jpg", DWObject.CurrentImageIndexInBuffer);
                    }
                    else if (document.getElementById("imgTypetiff").checked == true)
                        DWObject.SaveAllAsMultiPageTIFF("DynamicWebTWAIN.tiff", this._OnSuccess, this._OnFailure);
                    else if (document.getElementById("imgTypepdf").checked == true)
                        DWObject.SaveAllAsPDF("DynamicWebTWAIN.pdf", this._OnSuccess, this._OnFailure);
                }
            }
        },
        _LoadImage: function () {
            var DWObject = Dynamsoft.WebTwainEnv.GetWebTwain('dwtcontrolContainer');
            if (DWObject) {
                DWObject.IfShowFileDialog = true; // Open the system's file dialog to load image
                DWObject.LoadImageEx("", EnumDWT_ImageType.IT_ALL, this._OnSuccess, this._OnFailure); // Load images in all supported formats (.bmp, .jpg, .tif, .png, .pdf). sFun or fFun will be called after the operation
            }
        },

        // OnHttpUploadSuccess and OnHttpUploadFailure are callback functions.
        // OnHttpUploadSuccess is the callback function for successful uploads while OnHttpUploadFailure is for failed ones.
        _OnHttpUploadSuccess:function () {
            console.log('successful');
        },

        _OnHttpUploadFailure: function(errorCode, errorString, sHttpResponse) {
            alert(errorString + sHttpResponse);
        },
        _UploadImage: function () {
            var DWObject = Dynamsoft.WebTwainEnv.GetWebTwain('dwtcontrolContainer');
            if (DWObject) {
                // If no image in buffer, return the function
                if (DWObject.HowManyImagesInBuffer == 0)
                    return;

                var strHTTPServer = location.hostname; //The name of the HTTP server. For example: "www.dynamsoft.com";
                var CurrentPathName = unescape(location.pathname);
                var CurrentPath = CurrentPathName.substring(0, CurrentPathName.lastIndexOf("/") + 1);
                var strActionPage = CurrentPath;
                DWObject.IfSSL = false; // Set whether SSL is used
                DWObject.HTTPPort = location.port == "" ? 80 : location.port;

                var Digital = new Date();
                var uploadfilename = Digital.getMilliseconds(); // Uses milliseconds according to local time as the file name

                // Upload the image(s) to the server asynchronously
                if (document.getElementById("imgTypejpeg").checked == true) {
                    //If the current image is B&W
                    //1 is B&W, 8 is Gray, 24 is RGB
                    if (DWObject.GetImageBitDepth(DWObject.CurrentImageIndexInBuffer) == 1)
                        //If so, convert the image to Gray
                        DWObject.ConvertToGrayScale(DWObject.CurrentImageIndexInBuffer);
                    //Upload image in JPEG
                    DWObject.HTTPUploadThroughPost(strHTTPServer, DWObject.CurrentImageIndexInBuffer, strActionPage, uploadfilename + ".jpg", this._OnHttpUploadSuccess, this._OnHttpUploadFailure);
                }
                else if (document.getElementById("imgTypetiff").checked == true) {
                    DWObject.HTTPUploadAllThroughPostAsMultiPageTIFF(strHTTPServer, strActionPage, uploadfilename + ".tif", this._OnHttpUploadSuccess, this._OnHttpUploadFailure);
                }
                else if (document.getElementById("imgTypepdf").checked == true) {
                    DWObject.HTTPUploadAllThroughPostAsPDF(strHTTPServer, strActionPage, uploadfilename + ".pdf", this._OnHttpUploadSuccess, this._OnHttpUploadFailure);
                }
            }
        },
    });



    // core.action_registry.add('petstore.homepage', TestView);
    core.action_registry.add('twain_scanner', TwainContainer);
    return TwainContainer;
});

// core.action_registry.add('backend_dashboard', Dashboard);

// return Dashboard;