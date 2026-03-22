"""
Tozai Tours — Генератор КП
Запуск: python app.py  →  открыть http://localhost:5000
"""
import os
import io
import json
import zipfile
import traceback
from pathlib import Path
from flask import Flask, render_template, request, send_file, jsonify
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / '.env')

from rates_loader import load_japan_rates
from claude_generator import generate_program, refine_program
from excel_generator import create_excel
from ppt_generator import create_ppt
from brief_parser import parse_brief

app = Flask(__name__)


def _parse_params(data: dict) -> dict:
    twn = int(data.get('twn') or 0)
    sgl = int(data.get('sgl') or 0)
    # pax can be passed explicitly (e.g. from hidden field) or derived from rooms
    pax_from_rooms = twn * 2 + sgl
    pax = int(data.get('pax') or pax_from_rooms or 30)
    return {
        'company_name':       data.get('company_name', 'Компания').strip(),
        'pax':                pax,
        'days':               int(data.get('days', 4)),
        'dates':              data.get('dates', '').strip(),
        'hotel_level':        data.get('hotel_level', '4*'),
        'twn':                twn,
        'sgl':                sgl,
        'total_rooms':        twn + sgl,
        'pax_from_rooms':     pax_from_rooms,
        'hotel_a_name':       data.get('hotel_a_name', '').strip(),
        'hotel_a_rate':       float(data.get('hotel_a_rate') or 350),
        'hotel_b_name':       data.get('hotel_b_name', '').strip(),
        'hotel_b_rate':       float(data.get('hotel_b_rate') or 0),
        'event_type':         data.get('event_type', 'Инсентив'),
        'industry':           data.get('industry', '').strip(),
        'special_requests':   data.get('special_requests', '').strip(),
        'include_conference': data.get('include_conference') in (True, 'true', 'on', '1'),
        'conference_day':     int(data.get('conference_day') or 2),
    }


def _calc_budget(params: dict, services: list) -> dict:
    """Быстрый расчёт ориентировочной стоимости без генерации файла."""
    services_total = sum(s['total'] for s in services if s['type'] == 'service')

    pax = params['pax']
    twn = params['twn']
    sgl = params['sgl']
    nights = params['days'] - 1
    hotel_a_rate = float(params.get('hotel_a_rate') or 350)
    hotel_b_rate = float(params.get('hotel_b_rate') or 0)

    hotel_a_total = (twn + sgl) * nights * hotel_a_rate
    hotel_b_total = (twn + sgl) * nights * hotel_b_rate if hotel_b_rate else 0

    grand_total = services_total + hotel_a_total
    per_person = grand_total / pax if pax else 0

    return {
        'hotel':         round(hotel_a_total),   # backward compat — primary variant A
        'hotel_a':       round(hotel_a_total),
        'hotel_b':       round(hotel_b_total),
        'hotel_a_total': round(hotel_a_total),
        'hotel_b_total': round(hotel_b_total),
        'services':      round(services_total),
        'total':         round(grand_total),
        'per_person':    round(per_person),
    }


# ── Главная страница ──────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')


# ── Шаг 1: Черновик программы ────────────────────────────────────────────────

@app.route('/draft_program', methods=['POST'])
def draft_program():
    try:
        params = _parse_params(request.json)
        services = load_japan_rates(params['pax'], params['days'], params['include_conference'])
        content = generate_program(params)
        budget = _calc_budget(params, services)
        return jsonify({'ok': True, 'program': content, 'budget': budget})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e), 'traceback': traceback.format_exc()}), 500


# ── Шаг 1б: Корректировка программы ─────────────────────────────────────────

@app.route('/refine_program', methods=['POST'])
def refine():
    try:
        body = request.json
        params = _parse_params(body['params'])
        current = body['program']
        corrections = body.get('corrections', '').strip()
        if not corrections:
            return jsonify({'ok': True, 'program': current})

        updated = refine_program(params, current, corrections)
        services = load_japan_rates(params['pax'], params['days'], params['include_conference'])
        budget = _calc_budget(params, services)
        return jsonify({'ok': True, 'program': updated, 'budget': budget})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e), 'traceback': traceback.format_exc()}), 500


# ── Шаг 2: Скачать смету Excel ───────────────────────────────────────────────

@app.route('/download_excel', methods=['POST'])
def download_excel():
    try:
        body = request.json
        params = _parse_params(body['params'])
        content = body['program']
        services = load_japan_rates(params['pax'], params['days'], params['include_conference'])
        xlsx = create_excel(params, services, content)

        slug = _slug(params['company_name'])
        return send_file(
            io.BytesIO(xlsx),
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'Smeta_{slug}_Japan_{params["pax"]}pax.xlsx',
        )
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


# ── Шаг 3: Скачать презентацию PPT ───────────────────────────────────────────

@app.route('/download_ppt', methods=['POST'])
def download_ppt():
    try:
        body = request.json
        params = _parse_params(body['params'])
        content = body['program']
        services = load_japan_rates(params['pax'], params['days'], params['include_conference'])
        pptx = create_ppt(params, content, services)

        slug = _slug(params['company_name'])
        return send_file(
            io.BytesIO(pptx),
            mimetype='application/vnd.openxmlformats-officedocument.presentationml.presentation',
            as_attachment=True,
            download_name=f'Program_{slug}_Japan_{params["days"]}days.pptx',
        )
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


# ── Загрузка и разбор брифа ───────────────────────────────────────────────────

@app.route('/parse_brief', methods=['POST'])
def parse_brief_route():
    try:
        if 'brief' not in request.files:
            return jsonify({'ok': False, 'error': 'Файл не получен'}), 400
        f = request.files['brief']
        if not f.filename:
            return jsonify({'ok': False, 'error': 'Файл пустой'}), 400

        file_bytes = f.read()
        result = parse_brief(file_bytes, f.filename)

        if 'error' in result:
            return jsonify({'ok': False, 'error': result['error']}), 500

        return jsonify({'ok': True, 'fields': result})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e), 'traceback': traceback.format_exc()}), 500


# ── Утилиты ───────────────────────────────────────────────────────────────────

def _slug(name: str) -> str:
    return ''.join(c for c in name if c.isalnum() or c in ' _-')[:25].strip().replace(' ', '_')


if __name__ == '__main__':
    print('=' * 52)
    print('  TOZAI TOURS - Generator KP')
    print('  http://localhost:5000')
    print('=' * 52)
    app.run(debug=False, port=5000, host='0.0.0.0')
