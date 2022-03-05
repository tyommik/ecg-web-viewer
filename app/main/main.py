import json
from itertools import chain
import time

import matplotlib.pyplot as plt

from flask import Blueprint, render_template
from flask_login import login_required, current_user
from flask import Flask, render_template, redirect, url_for, make_response, jsonify, request

from utils import read_npy_data, resample_waveform
from app import db
from app.auth.auth import users

from rtypes import types_mapping, default_data, default_history
from config import DATASET_DIR

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/<uuid:index>', methods=['get'])
def file(index):
    return render_template('file.html', index=index)


@main.route('/find/<uuid:index>', methods=['get'])
def getlist(index):
    ecglist = db.query_by_uuid(index)
    if ecglist:
        data = [{"id": index, "title": f'{str(ecg["file_id"])[:8]} - {ecg["test_date"].strftime("%d-%m-%Y")}'} for idx, ecg in enumerate(ecglist)]
        return make_response(jsonify(data), 200)
    return make_response(jsonify([]), 404)


@main.route('/leads/<uuid:index>', methods=['get'])
def getleads(index):
    request = db.query_by_uuid(index)
    if len(request):
        rel_ecg_path = request[0].get("src_path")
        abs_ecg_path = DATASET_DIR / (rel_ecg_path + '.npy')
        try:
            leads = read_npy_data(str(abs_ecg_path))
            leads = [lead.tolist() for lead in leads]
        except FileNotFoundError as err:
            user = current_user.name
            # db.mask_as_done(index, user)
        else:
            return make_response(jsonify({'data': leads}), 200)
    return make_response(jsonify({'data': {}}), 500)


@main.route('/anno/<uuid:index>', methods=['POST'])
def setanno(index):
    form = request.form
    if form:
        try:
            txt = list(form.keys())[0]
            data = json.loads(txt)
        except json.decoder.JSONDecodeError as err:
            return make_response(jsonify("", 500))
        else:

            for group in data:
                for view in group["group_data"]:
                    view["label"] = types_mapping[view["name"]]
            db.update_anno(index, current_user.name, json.dumps(data))
    return make_response(jsonify("", 200))


@main.route('/anno/<uuid:index>', methods=['GET'])
def getanno(index):
    query_result = db.query_report_by_uuid(index)
    if query_result:
        one_result = query_result[0]
        sex = "Мужской" if one_result['sex'] == 'm' else "Женский"
        age = one_result['age']
        report = f"Пол: {sex}, возраст: {age}.<br><br><b>Заключение врача:</b> {one_result['report']}" \
            if one_result['report'] else f"Пол: {sex}, возраст: {age}.<br><br><b>Заключение врача остутствует</b>"

        data = json.loads("{}")

        if not data:
            data = default_data.copy()
        else:
            data = json.loads(data)

        return make_response(jsonify({'data': data, 'report': report}), 200)
