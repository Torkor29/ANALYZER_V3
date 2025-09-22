#!/usr/bin/env python3
"""
Application web pour l'Analyseur de Trading
Interface simple et professionnelle pour analyser les fichiers de trading
"""

from flask import Flask, request, jsonify, send_file, send_from_directory, url_for, flash, redirect
from flask_cors import CORS
import os
import uuid
import threading
import time
from datetime import datetime
import shutil
from werkzeug.utils import secure_filename
from trading_analyzer_unified import TradingAnalyzer
import pandas as pd

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})
app.secret_key = os.environ.get('SECRET_KEY', 'trading-analyzer-secret-key-2025')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # Limite de 50MB

# Configuration des dossiers
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
REPORTS_FOLDER = os.path.join(os.getcwd(), 'reports')
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

# Créer les dossiers s'ils n'existent pas
for folder in [UPLOAD_FOLDER, REPORTS_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# Stockage des tâches en cours
task_status = {}

def allowed_file(filename):
    """Vérifie si le fichier est autorisé"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def cleanup_old_files():
    """Nettoie les anciens fichiers (plus de 24h)"""
    current_time = time.time()
    for folder in [UPLOAD_FOLDER, REPORTS_FOLDER]:
        if os.path.exists(folder):
            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)
                if os.path.isfile(file_path):
                    if current_time - os.path.getctime(file_path) > 24 * 3600:  # 24 heures
                        try:
                            os.remove(file_path)
                        except Exception:
                            pass

def process_files_background(task_id, file_paths, filter_type, solde_initial, multiplier):
    """Traite les fichiers en arrière-plan"""
    try:
        # Initialiser le statut de la tâche
        task_status[task_id]['progress'] = 10
        task_status[task_id]['message'] = 'Initialisation de l\'analyseur...'
        
        # Créer l'analyseur
        analyzer = TradingAnalyzer(solde_initial=solde_initial)
        
        # Traiter les fichiers
        task_status[task_id]['progress'] = 20
        task_status[task_id]['message'] = 'Traitement des fichiers...'
        
        df_final = analyzer.process_files(file_paths, task_id, task_status, filter_type)

        # Appliquer le multiplicateur sur les profits et pips puis recalculer les cumuls
        try:
            m = float(multiplier or 1.0)
        except Exception:
            m = 1.0
        if m != 1.0 and df_final is not None and len(df_final) > 0:
            if 'Profit' in df_final.columns:
                df_final['Profit'] = df_final['Profit'].astype(float) * m
            if 'Profit_pips' in df_final.columns:
                try:
                    df_final['Profit_pips'] = df_final['Profit_pips'].astype(float) * m
                except Exception:
                    pass

            # Recalcul cumuls en ordre chronologique
            try:
                if "Heure d'ouverture" in df_final.columns and 'Profit' in df_final.columns:
                    tmp = df_final.copy()
                    tmp['__dt'] = pd.to_datetime(tmp["Heure d'ouverture"], errors='coerce')
                    tmp = tmp[tmp['__dt'].notna()].sort_values('__dt')
                    tmp['__cum_profit'] = tmp['Profit'].astype(float).cumsum()
                    df_final.loc[tmp.index, 'Profit_cumule'] = tmp['__cum_profit']
                    if 'Profit_pips' in tmp.columns:
                        tmp['__cum_pips'] = tmp['Profit_pips'].astype(float).cumsum()
                        df_final.loc[tmp.index, 'Profit_pips_cumule'] = tmp['__cum_pips']
                    # solde cumulé
                    df_final.loc[tmp.index, 'Solde_cumule'] = solde_initial + tmp['__cum_profit']
            except Exception:
                pass
        
        if df_final is None or len(df_final) == 0:
            task_status[task_id]['success'] = False
            task_status[task_id]['error'] = 'Aucune donnée valide trouvée dans les fichiers'
            task_status[task_id]['progress'] = 100
            return
        
        # Conserver le DataFrame pour filtres temps réel (mémoire only)
        task_status[task_id]['_df'] = df_final
        task_status[task_id]['solde_initial'] = solde_initial

        # Créer le rapport Excel
        task_status[task_id]['progress'] = 85
        task_status[task_id]['message'] = 'Génération du rapport Excel...'
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        rapport_path = analyzer.create_excel_report(df_final, REPORTS_FOLDER, timestamp, filter_type)

        # Agrégations pour graphiques côté Web
        try:
            aggs = analyzer.calculer_agregations_graphes(df_final)
            sessions = analyzer.calculer_performance_par_session(df_final)
        except Exception:
            aggs = {}
            sessions = {}
        
        # Calculer les statistiques finales
        total_trades = len(df_final)
        profit_total = df_final['Profit'].sum()
        profit_compose = df_final['Profit_cumule'].iloc[-1] if len(df_final) > 0 else 0
        pips_totaux = df_final['Profit_pips_cumule'].iloc[-1] if len(df_final) > 0 else 0
        solde_final = df_final['Solde_cumule'].iloc[-1] if len(df_final) > 0 else solde_initial
        rendement_pct = ((solde_final - solde_initial) / solde_initial * 100)
        
        trades_gagnants = len(df_final[df_final["Profit"] > 0])
        trades_perdants = len(df_final[df_final["Profit"] < 0])
        taux_reussite = (trades_gagnants / (trades_gagnants + trades_perdants) * 100) if (trades_gagnants + trades_perdants) > 0 else 0
        
        # Drawdown maximum
        drawdown_max = df_final['Drawdown_pct'].max() if 'Drawdown_pct' in df_final.columns else 0
        
        # Construire série d'équity (solde_initial + cumul profits)
        evolution_equity = []
        try:
            temp = df_final.copy()
            if "Heure d'ouverture" in temp.columns and 'Profit' in temp.columns:
                temp['__dt'] = pd.to_datetime(temp["Heure d'ouverture"], errors='coerce')
                temp = temp[temp['__dt'].notna()].sort_values('__dt')
                cumul = float(solde_initial)
                for _, r in temp.iterrows():
                    cumul += float(r['Profit']) if pd.notna(r['Profit']) else 0.0
                    evolution_equity.append({'date': r['__dt'].isoformat(), 'solde': round(cumul, 2)})
        except Exception:
            pass

        # Finaliser la tâche
        task_status[task_id]['success'] = True
        task_status[task_id]['progress'] = 100
        task_status[task_id]['message'] = 'Analyse terminée avec succès!'
        task_status[task_id]['report_url'] = f"/download_report/{os.path.basename(rapport_path)}"
        task_status[task_id]['statistics'] = {
            'total_trades': total_trades,
            'profit_total': round(profit_total, 2),
            'profit_compose': round(profit_compose, 2),
            'pips_totaux': round(pips_totaux, 2),
            'solde_final': round(solde_final, 2),
            'rendement_pct': round(rendement_pct, 2),
            'solde_initial': round(solde_initial, 2),
            'trades_gagnants': trades_gagnants,
            'trades_perdants': trades_perdants,
            'taux_reussite': round(taux_reussite, 1),
            'drawdown_max': round(drawdown_max, 2),
            # Exposer les agrégations essentielles (convertir en structures JSON-sérialisables)
            'heures_in_counts': aggs.get('heures_in_counts').to_dict() if aggs.get('heures_in_counts') is not None and hasattr(aggs.get('heures_in_counts'), 'to_dict') else {},
            'heures_out_counts': aggs.get('heures_out_counts').to_dict() if aggs.get('heures_out_counts') is not None and hasattr(aggs.get('heures_out_counts'), 'to_dict') else {},
            'profits_par_heure_out': aggs.get('profits_par_heure_out').to_dict() if aggs.get('profits_par_heure_out') is not None and hasattr(aggs.get('profits_par_heure_out'), 'to_dict') else {},
            'profits_par_jour_out': aggs.get('profits_par_jour_out').to_dict() if aggs.get('profits_par_jour_out') is not None and hasattr(aggs.get('profits_par_jour_out'), 'to_dict') else {},
            'profits_par_mois_out': aggs.get('profits_par_mois_out').to_dict() if aggs.get('profits_par_mois_out') is not None and hasattr(aggs.get('profits_par_mois_out'), 'to_dict') else {},
            # Profits vs pertes (séparés)
            'profits_pos_par_heure_out': aggs.get('profits_pos_par_heure_out').to_dict() if aggs.get('profits_pos_par_heure_out') is not None and hasattr(aggs.get('profits_pos_par_heure_out'), 'to_dict') else {},
            'pertes_par_heure_out': aggs.get('pertes_par_heure_out').to_dict() if aggs.get('pertes_par_heure_out') is not None and hasattr(aggs.get('pertes_par_heure_out'), 'to_dict') else {},
            'pertes_abs_par_heure_out': aggs.get('pertes_abs_par_heure_out').to_dict() if aggs.get('pertes_abs_par_heure_out') is not None and hasattr(aggs.get('pertes_abs_par_heure_out'), 'to_dict') else {},
            'profits_pos_par_jour_out': aggs.get('profits_pos_par_jour_out').to_dict() if aggs.get('profits_pos_par_jour_out') is not None and hasattr(aggs.get('profits_pos_par_jour_out'), 'to_dict') else {},
            'pertes_par_jour_out': aggs.get('pertes_par_jour_out').to_dict() if aggs.get('pertes_par_jour_out') is not None and hasattr(aggs.get('pertes_par_jour_out'), 'to_dict') else {},
            'pertes_abs_par_jour_out': aggs.get('pertes_abs_par_jour_out').to_dict() if aggs.get('pertes_abs_par_jour_out') is not None and hasattr(aggs.get('pertes_abs_par_jour_out'), 'to_dict') else {},
            'profits_pos_par_mois_out': aggs.get('profits_pos_par_mois_out').to_dict() if aggs.get('profits_pos_par_mois_out') is not None and hasattr(aggs.get('profits_pos_par_mois_out'), 'to_dict') else {},
            'pertes_par_mois_out': aggs.get('pertes_par_mois_out').to_dict() if aggs.get('pertes_par_mois_out') is not None and hasattr(aggs.get('pertes_par_mois_out'), 'to_dict') else {},
            'pertes_abs_par_mois_out': aggs.get('pertes_abs_par_mois_out').to_dict() if aggs.get('pertes_abs_par_mois_out') is not None and hasattr(aggs.get('pertes_abs_par_mois_out'), 'to_dict') else {},
            'tp_par_heure': aggs.get('tp_par_heure').to_dict() if aggs.get('tp_par_heure') is not None and hasattr(aggs.get('tp_par_heure'), 'to_dict') else {},
            'sl_par_heure': aggs.get('sl_par_heure').to_dict() if aggs.get('sl_par_heure') is not None and hasattr(aggs.get('sl_par_heure'), 'to_dict') else {},
            'tp_par_jour': aggs.get('tp_par_jour').to_dict() if aggs.get('tp_par_jour') is not None and hasattr(aggs.get('tp_par_jour'), 'to_dict') else {},
            'sl_par_jour': aggs.get('sl_par_jour').to_dict() if aggs.get('sl_par_jour') is not None and hasattr(aggs.get('sl_par_jour'), 'to_dict') else {},
            'tp_par_mois': aggs.get('tp_par_mois').to_dict() if aggs.get('tp_par_mois') is not None and hasattr(aggs.get('tp_par_mois'), 'to_dict') else {},
            'sl_par_mois': aggs.get('sl_par_mois').to_dict() if aggs.get('sl_par_mois') is not None and hasattr(aggs.get('sl_par_mois'), 'to_dict') else {},
            'duree_moyenne_minutes': aggs.get('duree_moyenne_minutes') if aggs.get('duree_moyenne_minutes') is not None else None,
            'duree_mediane_minutes': aggs.get('duree_mediane_minutes') if aggs.get('duree_mediane_minutes') is not None else None,
            'evolution_somme_cumulee': aggs.get('evolution_somme_cumulee') if aggs.get('evolution_somme_cumulee') is not None else [],
            'evolution_equity': evolution_equity,
            # Sessions (Asie/Europe/Amérique)
            'sessions_total': sessions.get('sessions_total', {}),
            'sessions_par_pair': sessions.get('sessions_par_pair', {}),
            # Liste des paires disponibles (pour l'UI)
            'pairs': list(df_final['Symbole_ordre'].dropna().unique()) if 'Symbole_ordre' in df_final.columns else []
        }
        
        # Nettoyer les fichiers uploadés
        for file_path in file_paths:
            try:
                os.remove(file_path)
            except Exception:
                pass
                
    except Exception as e:
        task_status[task_id]['success'] = False
        task_status[task_id]['error'] = str(e)
        task_status[task_id]['progress'] = 100
        task_status[task_id]['message'] = f'Erreur: {str(e)}'

@app.route('/filter_stats/<task_id>', methods=['POST'])
def filter_stats(task_id):
    """Recalcule les agrégations pour un sous-ensemble (paires + intervalle de dates)."""
    if task_id not in task_status:
        return jsonify({'success': False, 'error': 'Tâche inconnue'}), 404
    if '_df' not in task_status[task_id] or task_status[task_id]['_df'] is None:
        return jsonify({'success': False, 'error': 'Données non disponibles en mémoire'}), 400
    try:
        payload = request.get_json(force=True, silent=True) or {}
        pairs = payload.get('pairs') or []
        date_start = payload.get('date_start')
        date_end = payload.get('date_end')

        df = task_status[task_id]['_df'].copy()
        # Filtre par paires
        if pairs and 'Symbole_ordre' in df.columns:
            df = df[df['Symbole_ordre'].isin(pairs)]
        # Filtre dates
        if 'Heure d\'ouverture' in df.columns:
            df['__dt'] = pd.to_datetime(df['Heure d\'ouverture'], errors='coerce')
            if date_start:
                try:
                    ds = pd.to_datetime(date_start)
                    df = df[df['__dt'] >= ds]
                except Exception:
                    pass
            if date_end:
                try:
                    de = pd.to_datetime(date_end) + pd.Timedelta(days=1)
                    df = df[df['__dt'] < de]
                except Exception:
                    pass
            df = df.drop(columns=['__dt'])

        analyzer = TradingAnalyzer()
        aggs = analyzer.calculer_agregations_graphes(df)
        sessions = analyzer.calculer_performance_par_session(df)

        # Recalcul intégral des statistiques
        stats = {
            'total_trades': int(len(df)),
            'profit_total': round(float(df['Profit'].sum()), 2) if 'Profit' in df.columns else 0.0,
            'profit_compose': 0.0,
            'pips_totaux': 0.0,
            'solde_final': 0.0,
            'rendement_pct': 0.0,
            'trades_gagnants': int((df['Profit'] > 0).sum()) if 'Profit' in df.columns else 0,
            'trades_perdants': int((df['Profit'] < 0).sum()) if 'Profit' in df.columns else 0,
            'taux_reussite': 0.0,
            'drawdown_max': 0.0,
            'heures_in_counts': aggs.get('heures_in_counts').to_dict() if aggs.get('heures_in_counts') is not None and hasattr(aggs.get('heures_in_counts'), 'to_dict') else {},
            'heures_out_counts': aggs.get('heures_out_counts').to_dict() if aggs.get('heures_out_counts') is not None and hasattr(aggs.get('heures_out_counts'), 'to_dict') else {},
            'profits_par_heure_out': aggs.get('profits_par_heure_out').to_dict() if aggs.get('profits_par_heure_out') is not None and hasattr(aggs.get('profits_par_heure_out'), 'to_dict') else {},
            'profits_par_jour_out': aggs.get('profits_par_jour_out').to_dict() if aggs.get('profits_par_jour_out') is not None and hasattr(aggs.get('profits_par_jour_out'), 'to_dict') else {},
            'profits_par_mois_out': aggs.get('profits_par_mois_out').to_dict() if aggs.get('profits_par_mois_out') is not None and hasattr(aggs.get('profits_par_mois_out'), 'to_dict') else {},
            'profits_pos_par_heure_out': aggs.get('profits_pos_par_heure_out').to_dict() if aggs.get('profits_pos_par_heure_out') is not None and hasattr(aggs.get('profits_pos_par_heure_out'), 'to_dict') else {},
            'pertes_abs_par_heure_out': aggs.get('pertes_abs_par_heure_out').to_dict() if aggs.get('pertes_abs_par_heure_out') is not None and hasattr(aggs.get('pertes_abs_par_heure_out'), 'to_dict') else {},
            'profits_pos_par_jour_out': aggs.get('profits_pos_par_jour_out').to_dict() if aggs.get('profits_pos_par_jour_out') is not None and hasattr(aggs.get('profits_pos_par_jour_out'), 'to_dict') else {},
            'pertes_abs_par_jour_out': aggs.get('pertes_abs_par_jour_out').to_dict() if aggs.get('pertes_abs_par_jour_out') is not None and hasattr(aggs.get('pertes_abs_par_jour_out'), 'to_dict') else {},
            'profits_pos_par_mois_out': aggs.get('profits_pos_par_mois_out').to_dict() if aggs.get('profits_pos_par_mois_out') is not None and hasattr(aggs.get('profits_pos_par_mois_out'), 'to_dict') else {},
            'pertes_abs_par_mois_out': aggs.get('pertes_abs_par_mois_out').to_dict() if aggs.get('pertes_abs_par_mois_out') is not None and hasattr(aggs.get('pertes_abs_par_mois_out'), 'to_dict') else {},
            'tp_par_heure': aggs.get('tp_par_heure').to_dict() if aggs.get('tp_par_heure') is not None and hasattr(aggs.get('tp_par_heure'), 'to_dict') else {},
            'sl_par_heure': aggs.get('sl_par_heure').to_dict() if aggs.get('sl_par_heure') is not None and hasattr(aggs.get('sl_par_heure'), 'to_dict') else {},
            'tp_par_jour': aggs.get('tp_par_jour').to_dict() if aggs.get('tp_par_jour') is not None and hasattr(aggs.get('tp_par_jour'), 'to_dict') else {},
            'sl_par_jour': aggs.get('sl_par_jour').to_dict() if aggs.get('sl_par_jour') is not None and hasattr(aggs.get('sl_par_jour'), 'to_dict') else {},
            'tp_par_mois': aggs.get('tp_par_mois').to_dict() if aggs.get('tp_par_mois') is not None and hasattr(aggs.get('tp_par_mois'), 'to_dict') else {},
            'sl_par_mois': aggs.get('sl_par_mois').to_dict() if aggs.get('sl_par_mois') is not None and hasattr(aggs.get('sl_par_mois'), 'to_dict') else {},
            'duree_moyenne_minutes': aggs.get('duree_moyenne_minutes'),
            'duree_mediane_minutes': aggs.get('duree_mediane_minutes'),
            'evolution_somme_cumulee': [],
            'sessions_total': sessions.get('sessions_total', {}),
            'sessions_par_pair': sessions.get('sessions_par_pair', {}),
            'pairs': list(df['Symbole_ordre'].dropna().unique()) if 'Symbole_ordre' in df.columns else []
        }

        # Recalcul cumuls/solde/drawdown/évolution
        if len(df) > 0 and 'Profit' in df.columns:
            temp = df.copy()
            temp['__dt'] = pd.to_datetime(temp.get("Heure d'ouverture"), errors='coerce')
            temp = temp[temp['__dt'].notna()].sort_values('__dt')
            temp['__cum_profit'] = temp['Profit'].cumsum()
            stats['profit_compose'] = round(float(temp['__cum_profit'].iloc[-1]), 2)

            if 'Profit_pips' in temp.columns:
                temp['__cum_pips'] = temp['Profit_pips'].cumsum()
                stats['pips_totaux'] = round(float(temp['__cum_pips'].iloc[-1]), 2)

            solde_initial = float(task_status.get(task_id, {}).get('solde_initial', 0) or 0)
            stats['solde_final'] = round(solde_initial + stats['profit_compose'], 2) if solde_initial else round(stats['profit_compose'], 2)
            stats['rendement_pct'] = round(((stats['solde_final'] - solde_initial) / solde_initial * 100) if solde_initial else 0, 2)

            equity = (solde_initial + temp['__cum_profit']) if solde_initial else temp['__cum_profit']
            peak = equity.cummax()
            dd = (peak - equity) / peak.replace(0, pd.NA) * 100
            stats['drawdown_max'] = round(float(dd.max(skipna=True) or 0), 2)

            denom = stats['trades_gagnants'] + stats['trades_perdants']
            stats['taux_reussite'] = round((stats['trades_gagnants'] / denom * 100) if denom else 0, 1)

            # Série d'équity (incluant solde initial)
            evolution = []
            cumul = float(solde_initial)
            for _, r in temp.iterrows():
                cumul += float(r['Profit']) if pd.notna(r['Profit']) else 0.0
                evolution.append({'date': r['__dt'].isoformat(), 'solde': round(cumul, 2)})
            stats['evolution_somme_cumulee'] = evolution
        else:
            # dataset vide => forcer zéros partout
            stats.update({
                'profit_compose': 0.0,
                'pips_totaux': 0.0,
                'solde_final': float(task_status.get(task_id, {}).get('solde_initial', 0) or 0),
                'rendement_pct': 0.0,
                'taux_reussite': 0.0,
                'drawdown_max': 0.0,
                'evolution_somme_cumulee': []
            })

        return jsonify({'success': True, 'statistics': stats})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def _dist_folder():
    return os.path.join(os.getcwd(), 'frontend', 'dist')

# --- SPA static serving (100% SPA) ---
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def spa(path: str):
    """Servez le build React si présent (frontend/dist). Sinon, exposez une info minimale."""
    dist = _dist_folder()
    index_path = os.path.join(dist, 'index.html')
    if os.path.exists(index_path):
        # Fichier statique demandé
        if path and os.path.exists(os.path.join(dist, path)):
            return send_from_directory(dist, path)
        # Fallback SPA
        return send_from_directory(dist, 'index.html')
    # Pas de build → simple page d'info
    return (
        "<html><body style='font-family:system-ui'>"
        "<h2>Frontend non compilé</h2>"
        "<p>Lancez le frontend en dev (Vite) sur <code>http://localhost:5173</code> ou exécutez <code>npm run build</code> dans <code>frontend/</code>.</p>"
        "</body></html>",
        200,
        {"Content-Type": "text/html"}
    )

# --- API aliases pour frontend React ---
@app.route('/api/health')
def api_health():
    return jsonify({"status": "ok"})

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    # délègue à la logique d'upload existante
    return upload_files()

@app.route('/api/status/<task_id>')
def api_status(task_id):
    return get_status(task_id)

@app.route('/api/report/<filename>')
def api_report(filename):
    return download_report(filename)

@app.route('/upload', methods=['POST'])
def upload_files():
    """Gère l'upload des fichiers et lance l'analyse"""
    try:
        # Vérifier les fichiers
        if 'files' not in request.files:
            return jsonify({'success': False, 'error': 'Aucun fichier sélectionné'})
        
        files = request.files.getlist('files')
        if not files or all(f.filename == '' for f in files):
            return jsonify({'success': False, 'error': 'Aucun fichier sélectionné'})
        
        # Récupérer les paramètres
        filter_type = request.form.get('filter_type', 'tous')
        if filter_type == 'tous':
            filter_type = None
        
        try:
            solde_initial = float(request.form.get('solde_initial', 10000))
        except ValueError:
            solde_initial = 10000

        try:
            multiplier = float(request.form.get('multiplier', 1))
        except ValueError:
            multiplier = 1
        
        # Sauvegarder les fichiers
        file_paths = []
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Ajouter un timestamp pour éviter les conflits
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{timestamp}_{filename}"
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(file_path)
                file_paths.append(file_path)
        
        if not file_paths:
            return jsonify({'success': False, 'error': 'Aucun fichier Excel valide trouvé'})
        
        # Créer une tâche
        task_id = str(uuid.uuid4())
        task_status[task_id] = {
            'progress': 0,
            'message': 'Initialisation...',
            'success': None,
            'error': None,
            'solde_initial': solde_initial,
            'multiplier': multiplier
        }
        
        # Lancer le traitement en arrière-plan
        thread = threading.Thread(
            target=process_files_background,
            args=(task_id, file_paths, filter_type, solde_initial, multiplier)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({'success': True, 'task_id': task_id})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/status/<task_id>')
def get_status(task_id):
    """Récupère le statut d'une tâche"""
    if task_id not in task_status:
        return jsonify({'error': 'Tâche non trouvée'}), 404

    # Copier le statut et retirer les objets non sérialisables
    status = dict(task_status[task_id])
    status.pop('df_final', None)
    status.pop('_df', None)
    return jsonify(status)

@app.route('/download_report/<filename>')
def download_report(filename):
    """Télécharge un rapport"""
    try:
        file_path = os.path.join(REPORTS_FOLDER, filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return "Fichier non trouvé", 404
    except Exception as e:
        return f"Erreur: {str(e)}", 500

@app.errorhandler(413)
def too_large(e):
    """Gère les erreurs de fichiers trop volumineux"""
    return jsonify({'success': False, 'error': 'Fichier trop volumineux (limite: 50MB)'}), 413

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV', 'development') == 'development'
    
    print("🚀 Lancement de l'application web Trading Analyzer...")
    print(f"📊 Interface disponible sur le port: {port}")
    print("💾 Rapports sauvegardés dans:", REPORTS_FOLDER)
    print("📁 Fichiers temporaires dans:", UPLOAD_FOLDER)
    
    app.run(debug=debug_mode, host='0.0.0.0', port=port)