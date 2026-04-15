"""
Cathay DMC — Генератор proposal
Запуск: python app.py  →  http://localhost:5001
"""
import io
import os
import sys
import json
import zipfile
import traceback
from pathlib import Path
from datetime import date, timedelta

# Фикс кодировки на Windows (cp1251 → utf-8)
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

from flask import Flask, render_template, request, send_file, jsonify
from dotenv import load_dotenv
from contextlib import contextmanager

@contextmanager
def _quiet():
    """Перехватывает stdout/stderr во время генерации — кодировка в web-контексте ненадёжна."""
    buf = io.StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    sys.stdout = sys.stderr = buf
    try:
        yield buf
    finally:
        sys.stdout, sys.stderr = old_out, old_err

load_dotenv(Path(__file__).parent / '.env')

sys.path.insert(0, str(Path(__file__).parent))
from generate_ppt import generate as gen_ppt
from generate_quote import generate as gen_quote
from text_generator import SAMPLE_PROPOSAL
from parse_brief import parse_brief

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024


_MONTHS_RU = [
    'января','февраля','марта','апреля','мая','июня',
    'июля','августа','сентября','октября','ноября','декабря'
]
_MONTHS_SHORT_RU = [
    'янв','фев','мар','апр','май','июн',
    'июл','авг','сен','окт','ноя','дек'
]


def _parse_params(data: dict) -> dict:
    pax_sgl = int(data.get('pax_sgl') or 0)
    pax_dbl = int(data.get('pax_dbl') or 0)
    pax_total = pax_sgl + pax_dbl * 2 or int(data.get('pax_total') or 35)

    # start_date: берём из поля date или пробуем распарсить строку дат
    start_date = None
    raw_sd = data.get('start_date', '').strip()
    if raw_sd:
        try:
            start_date = date.fromisoformat(raw_sd)
        except ValueError:
            pass

    duration_days = int(data.get('duration_days') or 0)

    return {
        'client':        data.get('client', 'Клиент').strip(),
        'agency':        data.get('agency', '').strip(),
        'pax_sgl':       pax_sgl,
        'pax_dbl':       pax_dbl,
        'pax_total':     pax_total,
        'destination':   data.get('destination', 'Шанхай').strip(),
        'start_date':    start_date,
        'duration_days': duration_days,
        'season':        data.get('season', '').strip(),
        'group_profile': data.get('group_profile', '').strip(),
        'conference':    data.get('conference') in (True, 'true', 'on', '1'),
        'manager':       data.get('manager', 'Менеджер').strip(),
        'use_ai_texts':  data.get('use_ai_texts') in (True, 'true', 'on', '1'),
    }


def _dates_string(start: date, duration: int) -> str:
    """Строит строку дат для обложки: 'Шанхай, 13–17 апреля 2026'."""
    if not start or not duration:
        return ''
    end = start + timedelta(days=duration - 1)
    if start.month == end.month:
        return f"{start.day}–{end.day} {_MONTHS_RU[start.month - 1]} {start.year}"
    else:
        return (f"{start.day} {_MONTHS_RU[start.month - 1]} "
                f"– {end.day} {_MONTHS_RU[end.month - 1]} {end.year}")


def _build_proposal(p: dict) -> dict:
    """Берёт SAMPLE_PROPOSAL за основу и подставляет данные из формы."""
    import copy
    proposal = copy.deepcopy(SAMPLE_PROPOSAL)

    proposal['client']        = p['client']
    proposal['agency']        = p['agency']
    proposal['pax_total']     = p['pax_total']
    proposal['destination']   = p['destination']
    proposal['season']        = p['season'] or proposal.get('season', '')
    proposal['group_profile'] = p['group_profile'] or proposal.get('group_profile', '')
    proposal['duration_days'] = p['duration_days'] or len(proposal.get('days', []))

    # ── Строка дат для обложки (автоматически из start_date + duration) ───────
    proposal['dates'] = _dates_string(p.get('start_date'), p.get('duration_days'))

    # ── Обновляем даты каждого дня ────────────────────────────────────────────
    if p.get('start_date'):
        sd = p['start_date']
        for i, day in enumerate(proposal['days']):
            d = sd + timedelta(days=i)
            day['date'] = f"{d.day} {_MONTHS_RU[d.month - 1]}"

    return proposal


@app.route('/parse-brief', methods=['POST'])
def parse_brief_route():
    if 'file' not in request.files:
        return jsonify({'error': 'Файл не передан'}), 400

    f = request.files['file']
    if not f.filename:
        return jsonify({'error': 'Пустое имя файла'}), 400

    suffix = Path(f.filename).suffix.lower()
    if suffix not in ('.docx', '.pdf'):
        return jsonify({'error': 'Поддерживаются только .docx и .pdf'}), 400

    tmp_dir = Path(__file__).parent / '_output'
    tmp_dir.mkdir(exist_ok=True)
    tmp_path = str(tmp_dir / f'brief_upload{suffix}')
    f.save(tmp_path)

    try:
        with _quiet():
            result = parse_brief(tmp_path)
        return jsonify(result)
    except Exception as exc:
        return jsonify({'error': str(exc)}), 500
    finally:
        try:
            Path(tmp_path).unlink()
        except Exception:
            pass


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate():
    try:
        data   = request.form.to_dict()
        p      = _parse_params(data)
        output = data.get('output', 'both')   # 'ppt', 'excel', 'both'

        proposal = _build_proposal(p)

        # ── Имена файлов ─────────────────────────────────────────────────────
        today   = date.today().strftime('%d%b%Y').upper()
        code    = f"{p['client'].upper().replace(' ', '-')}-{p['pax_total']}PAX"
        ppt_name  = f"Proposal-{code}-{today}.pptx"
        xlsx_name = f"Quote-{code}-{today}.xlsx"

        # ── Временные файлы ──────────────────────────────────────────────────
        tmp_dir = Path(__file__).parent / '_output'
        tmp_dir.mkdir(exist_ok=True)
        ppt_path  = str(tmp_dir / ppt_name)
        xlsx_path = str(tmp_dir / xlsx_name)

        # ── Генерация ─────────────────────────────────────────────────────────
        if output in ('ppt', 'both'):
            with _quiet():
                gen_ppt(filename=ppt_path, proposal=proposal, use_ai_texts=p['use_ai_texts'])

        if output in ('excel', 'both'):
            with _quiet():
                gen_quote(
                    filename=xlsx_path,
                    params={
                        'code':       code,
                        'client':     p['client'],
                        'agency':     p['agency'],
                        'pax_sgl':    p['pax_sgl'],
                        'pax_dbl':    p['pax_dbl'],
                        'pax_total':  p['pax_total'],
                        'conference': p['conference'],
                        'issued':     date.today(),
                        'valid':      date(date.today().year,
                                          date.today().month,
                                          min(date.today().day + 7, 28)),
                    }
                )

        # ── Отдаём файл(ы) ────────────────────────────────────────────────────
        if output == 'ppt':
            return send_file(ppt_path, as_attachment=True, download_name=ppt_name)

        if output == 'excel':
            return send_file(xlsx_path, as_attachment=True, download_name=xlsx_name)

        # оба → ZIP
        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, 'w', zipfile.ZIP_DEFLATED) as zf:
            if Path(ppt_path).exists():
                zf.write(ppt_path,  ppt_name)
            if Path(xlsx_path).exists():
                zf.write(xlsx_path, xlsx_name)
        zip_buf.seek(0)
        zip_name = f"Proposal-{code}-{today}.zip"
        return send_file(zip_buf, as_attachment=True,
                         download_name=zip_name,
                         mimetype='application/zip')

    except Exception as exc:
        tb = traceback.format_exc()
        return jsonify({'error': str(exc), 'traceback': tb}), 500


if __name__ == '__main__':
    print("Cathay DMC — запуск сервера на http://localhost:5001")
    app.run(debug=True, port=5002, use_reloader=False)
