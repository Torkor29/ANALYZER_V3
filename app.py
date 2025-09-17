#!/usr/bin/env python3
"""
Application web pour l'Analyseur de Trading
Interface simple et professionnelle pour analyser les fichiers de trading
"""

from flask import Flask, render_template, request, jsonify, send_file, url_for, flash, redirect
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

def process_files_background(task_id, file_paths, filter_type, solde_initial):
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
        
        if df_final is None or len(df_final) == 0:
            task_status[task_id]['success'] = False
            task_status[task_id]['error'] = 'Aucune donnée valide trouvée dans les fichiers'
            task_status[task_id]['progress'] = 100
            return
        
        # Conserver le DataFrame pour filtres temps réel (mémoire only)
        task_status[task_id]['_df'] = df_final

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

        # Re-bâtir un objet statistics minimal pour réutiliser showResults côté web
        stats = {
            'total_trades': len(df),
            'profit_total': round(df['Profit'].sum(), 2) if 'Profit' in df.columns else 0,
            'profit_compose': round(df['Profit_cumule'].iloc[-1], 2) if 'Profit_cumule' in df.columns and len(df) > 0 else 0,
            'pips_totaux': round(df['Profit_pips_cumule'].iloc[-1], 2) if 'Profit_pips_cumule' in df.columns and len(df) > 0 else 0,
            'solde_final': round(df['Solde_cumule'].iloc[-1], 2) if 'Solde_cumule' in df.columns and len(df) > 0 else 0,
            'rendement_pct': 0,
            'trades_gagnants': int((df['Profit'] > 0).sum()) if 'Profit' in df.columns else 0,
            'trades_perdants': int((df['Profit'] < 0).sum()) if 'Profit' in df.columns else 0,
            'taux_reussite': 0,
            'drawdown_max': float(df.get('Drawdown_pct', pd.Series([0])).max()) if 'Drawdown_pct' in df.columns else 0,
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
            'evolution_somme_cumulee': aggs.get('evolution_somme_cumulee') or [],
            'sessions_total': sessions.get('sessions_total', {}),
            'sessions_par_pair': sessions.get('sessions_par_pair', {}),
            'pairs': list(df['Symbole_ordre'].dropna().unique()) if 'Symbole_ordre' in df.columns else []
        }
        # recompute dependent metrics
        try:
            if stats['solde_final'] and 'Profit' in df.columns and len(df) > 0:
                solde_initial = float(df['Solde_cumule'].iloc[0]) if 'Solde_cumule' in df.columns else 0
                stats['rendement_pct'] = round(((stats['solde_final'] - solde_initial) / solde_initial * 100) if solde_initial else 0, 2)
            denom = stats['trades_gagnants'] + stats['trades_perdants']
            stats['taux_reussite'] = round((stats['trades_gagnants'] / denom * 100) if denom else 0, 1)
        except Exception:
            pass

        return jsonify({'success': True, 'statistics': stats})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/')
def index():
    """Page d'accueil"""
    cleanup_old_files()
    return render_template('index.html')

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
            'error': None
        }
        
        # Lancer le traitement en arrière-plan
        thread = threading.Thread(
            target=process_files_background,
            args=(task_id, file_paths, filter_type, solde_initial)
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