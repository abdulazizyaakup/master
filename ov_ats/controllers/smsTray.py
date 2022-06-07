# -*- coding: utf-8 -*-
import base64
import os, json
# import pandas as pd
import lxml
import requests
import time
from multiprocessing import Pool
import werkzeug.exceptions
import werkzeug.urls
import werkzeug.wrappers
import urllib
import logging

from datetime import datetime
from odoo import fields, http, tools, _
from odoo.http import request
from odoo.addons.website_form.controllers.main import WebsiteForm
from odoo.addons.http_routing.models.ir_http import slug
from urllib.parse import quote
from urllib.request import urlopen, Request

class SaveAttachment(http.Controller):
    