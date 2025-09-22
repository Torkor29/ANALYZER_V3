#!/usr/bin/env python3
"""
Interface graphique moderne pour le Trading Analyzer
Design épuré avec correction de l'erreur Excel
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
from datetime import datetime
import subprocess
import webbrowser
from pathlib import Path

# Import de notre analyseur
from trading_analyzer_improved import TradingAnalyzerImproved

class ModernTradingAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🚀 Trading Analyzer Pro")
        self.root.geometry("900x700")
        self.root.configure(bg='#2c3e50')
        
        # Variables
        self.selected_files = []
        self.analyzer = TradingAnalyzerImproved(solde_initial=10000)
        self.task_status = {'current_task': {'progress': 0, 'message': 'En attente...'}}
        
        # Configuration du style moderne
        self.setup_modern_styles()
        
        # Création de l'interface
        self.create_modern_widgets()
        
        # Centrer la fenêtre
        self.center_window()
    
    def setup_modern_styles(self):
        """Configure les styles modernes"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configuration des couleurs modernes
        style.configure('Modern.TFrame', background='#34495e')
        style.configure('Modern.TLabel', 
                       font=('Segoe UI', 10),
                       foreground='#ecf0f1',
                       background='#34495e')
        
        style.configure('Title.TLabel', 
                       font=('Segoe UI', 18, 'bold'),
                       foreground='#3498db',
                       background='#2c3e50')
        
        style.configure('Header.TLabel', 
                       font=('Segoe UI', 12, 'bold'),
                       foreground='#ecf0f1',
                       background='#34495e')
        
        style.configure('Info.TLabel', 
                       font=('Segoe UI', 9),
                       foreground='#bdc3c7',
                       background='#34495e')
        
        # Style pour les boutons modernes
        style.configure('Modern.TButton', 
                       font=('Segoe UI', 10, 'bold'),
                       padding=12,
                       background='#3498db',
                       foreground='white')
        
        style.map('Modern.TButton',
                 background=[('active', '#2980b9')])
        
        # Style pour la barre de progression moderne
        style.configure('Modern.Horizontal.TProgressbar',
                       troughcolor='#34495e',
                       background='#27ae60',
                       bordercolor='#27ae60',
                       lightcolor='#27ae60',
                       darkcolor='#27ae60')
        
        # Style pour les combobox modernes
        style.configure('Modern.TCombobox',
                       font=('Segoe UI', 10),
                       fieldbackground='#ecf0f1',
                       background='#ecf0f1')
        
        # Style pour les entry modernes
        style.configure('Modern.TEntry',
                       font=('Segoe UI', 10),
                       fieldbackground='#ecf0f1',
                       background='#ecf0f1')
    
    def create_modern_widgets(self):
        """Crée tous les widgets avec un design moderne"""
        
        # Frame principal avec padding
        main_frame = ttk.Frame(self.root, style='Modern.TFrame', padding="25")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configuration du grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # === TITRE MODERNE ===
        title_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        title_frame.grid(row=0, column=0, columnspan=3, pady=(0, 30), sticky=(tk.W, tk.E))
        
        title_label = ttk.Label(title_frame, 
                               text="🚀 Trading Analyzer Pro", 
                               style='Title.TLabel')
        title_label.pack()
        
        subtitle_label = ttk.Label(title_frame,
                                  text="Analyse professionnelle de vos trades",
                                  style='Info.TLabel')
        subtitle_label.pack(pady=(5, 0))
        
        # === SECTION SÉLECTION DE FICHIERS MODERNE ===
        files_frame = self.create_section_frame(main_frame, "📁 Sélection des fichiers Excel", 1)
        
        # Bouton moderne pour sélectionner les fichiers
        self.select_files_btn = ttk.Button(files_frame, 
                                          text="📂 Sélectionner des fichiers Excel",
                                          command=self.select_files,
                                          style='Modern.TButton')
        self.select_files_btn.pack(pady=(0, 15))
        
        # Frame pour la liste des fichiers
        list_frame = ttk.Frame(files_frame, style='Modern.TFrame')
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Liste des fichiers avec style moderne
        self.files_listbox = tk.Listbox(list_frame, 
                                       height=6, 
                                       bg='#ecf0f1',
                                       fg='#2c3e50',
                                       font=('Segoe UI', 9),
                                       selectmode=tk.EXTENDED,
                                       relief=tk.FLAT,
                                       bd=0)
        self.files_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar moderne
        files_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.files_listbox.yview)
        files_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.files_listbox.configure(yscrollcommand=files_scrollbar.set)
        
        # Boutons de gestion modernes
        files_buttons_frame = ttk.Frame(files_frame, style='Modern.TFrame')
        files_buttons_frame.pack(pady=(0, 15))
        
        ttk.Button(files_buttons_frame, 
                  text="🗑️ Supprimer sélection",
                  command=self.remove_selected_files,
                  style='Modern.TButton').pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(files_buttons_frame, 
                  text="🗑️ Vider la liste",
                  command=self.clear_files_list,
                  style='Modern.TButton').pack(side=tk.LEFT)
        
        # Label pour le nombre de fichiers
        self.files_count_label = ttk.Label(files_frame, 
                                          text="Aucun fichier sélectionné",
                                          style='Info.TLabel')
        self.files_count_label.pack()
        
        # === SECTION CONFIGURATION MODERNE ===
        config_frame = self.create_section_frame(main_frame, "⚙️ Configuration", 2)
        
        # Solde initial avec style moderne
        solde_frame = ttk.Frame(config_frame, style='Modern.TFrame')
        solde_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(solde_frame, text="💰 Solde initial (€):", style='Header.TLabel').pack(anchor=tk.W)
        
        self.solde_var = tk.StringVar(value="10000")
        solde_entry = ttk.Entry(solde_frame, 
                               textvariable=self.solde_var, 
                               width=20,
                               style='Modern.TEntry')
        solde_entry.pack(anchor=tk.W, pady=(5, 0))
        
        # Type d'analyse avec style moderne
        analysis_frame = ttk.Frame(config_frame, style='Modern.TFrame')
        analysis_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(analysis_frame, text="📊 Type d'analyse:", style='Header.TLabel').pack(anchor=tk.W)
        
        self.analysis_type = tk.StringVar(value="tous")
        analysis_combo = ttk.Combobox(analysis_frame, 
                                     textvariable=self.analysis_type,
                                     values=["tous", "forex", "autres"],
                                     state="readonly",
                                     width=20,
                                     style='Modern.TCombobox')
        analysis_combo.pack(anchor=tk.W, pady=(5, 0))
        
        # Aide contextuelle moderne
        help_frame = ttk.Frame(config_frame, style='Modern.TFrame')
        help_frame.pack(fill=tk.X)
        
        help_text = """• Tous: Analyse complète de tous les instruments
• Forex: Paires de devises uniquement  
• Autres: Métaux, indices, crypto, énergie, actions"""
        
        help_label = ttk.Label(help_frame, 
                              text=help_text,
                              style='Info.TLabel',
                              justify=tk.LEFT)
        help_label.pack(anchor=tk.W)
        
        # === SECTION ANALYSE MODERNE ===
        analysis_section_frame = self.create_section_frame(main_frame, "🔍 Analyse", 3)
        
        # Bouton d'analyse moderne
        self.analyze_btn = ttk.Button(analysis_section_frame, 
                                     text="🚀 Lancer l'analyse",
                                     command=self.start_analysis,
                                     style='Modern.TButton')
        self.analyze_btn.pack(pady=(0, 20))
        
        # Barre de progression moderne
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(analysis_section_frame, 
                                           variable=self.progress_var,
                                           maximum=100,
                                           style='Modern.Horizontal.TProgressbar',
                                           length=400)
        self.progress_bar.pack(pady=(0, 15))
        
        # Label de statut moderne
        self.status_label = ttk.Label(analysis_section_frame, 
                                     text="En attente...",
                                     style='Info.TLabel')
        self.status_label.pack()
        
        # === SECTION RÉSULTATS MODERNE ===
        results_frame = self.create_section_frame(main_frame, "📊 Résultats", 4)
        
        # Boutons de résultats modernes
        results_buttons_frame = ttk.Frame(results_frame, style='Modern.TFrame')
        results_buttons_frame.pack(pady=(0, 15))
        
        self.open_report_btn = ttk.Button(results_buttons_frame, 
                                         text="📄 Ouvrir le rapport Excel",
                                         command=self.open_report,
                                         state='disabled',
                                         style='Modern.TButton')
        self.open_report_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.open_folder_btn = ttk.Button(results_buttons_frame, 
                                         text="📁 Ouvrir le dossier des rapports",
                                         command=self.open_reports_folder,
                                         state='disabled',
                                         style='Modern.TButton')
        self.open_folder_btn.pack(side=tk.LEFT)
        
        # Label pour le chemin du rapport
        self.report_path_label = ttk.Label(results_frame, 
                                          text="Aucun rapport généré",
                                          style='Info.TLabel')
        self.report_path_label.pack()
        
        # === SECTION STATISTIQUES MODERNE ===
        stats_frame = self.create_section_frame(main_frame, "📈 Statistiques rapides", 5)
        
        # Labels pour les statistiques avec design moderne
        self.stats_labels = {}
        stats_info = [
            ("total_trades", "Total trades:"),
            ("trades_gagnants", "Trades gagnants:"),
            ("trades_perdants", "Trades perdants:"),
            ("taux_reussite", "Taux de réussite:"),
            ("profit_total", "Profit total:"),
            ("solde_final", "Solde final:")
        ]
        
        # Créer une grille pour les statistiques
        for i, (key, text) in enumerate(stats_info):
            row = i // 2
            col = (i % 2) * 2
            
            ttk.Label(stats_frame, text=text, style='Header.TLabel').grid(row=row, column=col, sticky=tk.W, padx=(0, 10), pady=2)
            self.stats_labels[key] = ttk.Label(stats_frame, text="--", style='Info.TLabel')
            self.stats_labels[key].grid(row=row, column=col+1, sticky=tk.W, pady=2)
    
    def create_section_frame(self, parent, title, row):
        """Crée une section avec titre moderne"""
        section_frame = ttk.LabelFrame(parent, text=title, padding="20")
        section_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        section_frame.configure(style='Modern.TFrame')
        return section_frame
    
    def center_window(self):
        """Centre la fenêtre sur l'écran"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def select_files(self):
        """Ouvre le dialogue de sélection de fichiers"""
        files = filedialog.askopenfilenames(
            title="Sélectionner les fichiers Excel",
            filetypes=[
                ("Fichiers Excel", "*.xlsx *.xls"),
                ("Tous les fichiers", "*.*")
            ]
        )
        
        if files:
            for file in files:
                if file not in self.selected_files:
                    self.selected_files.append(file)
                    self.files_listbox.insert(tk.END, os.path.basename(file))
            
            self.update_files_count()
    
    def remove_selected_files(self):
        """Supprime les fichiers sélectionnés de la liste"""
        selected_indices = self.files_listbox.curselection()
        for index in reversed(selected_indices):
            self.files_listbox.delete(index)
            self.selected_files.pop(index)
        
        self.update_files_count()
    
    def clear_files_list(self):
        """Vide complètement la liste des fichiers"""
        self.files_listbox.delete(0, tk.END)
        self.selected_files.clear()
        self.update_files_count()
    
    def update_files_count(self):
        """Met à jour le label du nombre de fichiers"""
        count = len(self.selected_files)
        if count == 0:
            self.files_count_label.config(text="Aucun fichier sélectionné")
        elif count == 1:
            self.files_count_label.config(text="1 fichier sélectionné")
        else:
            self.files_count_label.config(text=f"{count} fichiers sélectionnés")
    
    def start_analysis(self):
        """Lance l'analyse dans un thread séparé"""
        if not self.selected_files:
            messagebox.showwarning("Attention", "Veuillez sélectionner au moins un fichier Excel.")
            return
        
        try:
            solde_initial = float(self.solde_var.get())
        except ValueError:
            messagebox.showerror("Erreur", "Le solde initial doit être un nombre valide.")
            return
        
        # Désactiver les boutons pendant l'analyse
        self.analyze_btn.config(state='disabled')
        self.select_files_btn.config(state='disabled')
        
        # Réinitialiser la barre de progression
        self.progress_var.set(0)
        self.status_label.config(text="Démarrage de l'analyse...")
        
        # Lancer l'analyse dans un thread séparé
        analysis_thread = threading.Thread(target=self.run_analysis, args=(solde_initial,))
        analysis_thread.daemon = True
        analysis_thread.start()
    
    def run_analysis(self, solde_initial):
        """Exécute l'analyse (dans un thread séparé)"""
        try:
            # Créer l'analyseur avec le solde initial
            self.analyzer = TradingAnalyzerImproved(solde_initial=solde_initial)
            
            # Déterminer le filtre selon le type d'analyse
            analysis_type = self.analysis_type.get()
            if analysis_type == "forex":
                instrument_filter = "forex"
            elif analysis_type == "autres":
                instrument_filter = "autres"
            else:
                instrument_filter = None
            
            # Simuler le suivi de tâche
            task_id = "gui_analysis"
            self.task_status = {task_id: {'progress': 0, 'message': 'Démarrage...'}}
            
            # Lancer l'analyse
            df_result = self.analyzer.process_files(
                self.selected_files,
                task_id,
                self.task_status,
                instrument_filter
            )
            
            if df_result is not None:
                # Créer le dossier des rapports
                reports_folder = "reports"
                os.makedirs(reports_folder, exist_ok=True)
                
                # Générer le timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                # Créer le rapport Excel
                self.report_path = self.analyzer.create_excel_report(
                    df_result,
                    reports_folder,
                    timestamp,
                    instrument_filter
                )
                
                # Calculer les statistiques rapides
                self.calculate_quick_stats(df_result)
                
                # Mettre à jour l'interface dans le thread principal
                self.root.after(0, self.analysis_completed, True)
            else:
                self.root.after(0, self.analysis_completed, False)
                
        except Exception as e:
            error_msg = f"Erreur lors de l'analyse: {str(e)}"
            self.root.after(0, lambda: self.show_error(error_msg))
    
    def analysis_completed(self, success):
        """Appelé quand l'analyse est terminée"""
        if success:
            self.status_label.config(text="✅ Analyse terminée avec succès!")
            self.progress_var.set(100)
            
            # Activer les boutons de résultats
            self.open_report_btn.config(state='normal')
            self.open_folder_btn.config(state='normal')
            
            # Mettre à jour le label du chemin
            self.report_path_label.config(text=f"Rapport: {os.path.basename(self.report_path)}")
            
            messagebox.showinfo("Succès", f"Analyse terminée!\n\nRapport créé: {os.path.basename(self.report_path)}")
        else:
            self.status_label.config(text="❌ Échec de l'analyse")
            messagebox.showerror("Erreur", "L'analyse a échoué. Vérifiez vos fichiers.")
        
        # Réactiver les boutons
        self.analyze_btn.config(state='normal')
        self.select_files_btn.config(state='normal')
    
    def calculate_quick_stats(self, df):
        """Calcule les statistiques rapides"""
        total_trades = len(df)
        trades_gagnants = len(df[df["Profit"] > 0])
        trades_perdants = len(df[df["Profit"] < 0])
        trades_avec_resultat = trades_gagnants + trades_perdants
        
        taux_reussite = (trades_gagnants / trades_avec_resultat * 100) if trades_avec_resultat > 0 else 0
        profit_total = df['Profit'].sum()
        solde_final = df['Solde_cumule'].iloc[-1] if len(df) > 0 else self.analyzer.solde_initial
        
        # Mettre à jour les labels dans le thread principal
        self.root.after(0, lambda: self.update_stats_labels(
            total_trades, trades_gagnants, trades_perdants, 
            taux_reussite, profit_total, solde_final
        ))
    
    def update_stats_labels(self, total_trades, trades_gagnants, trades_perdants, 
                          taux_reussite, profit_total, solde_final):
        """Met à jour les labels des statistiques"""
        self.stats_labels["total_trades"].config(text=str(total_trades))
        self.stats_labels["trades_gagnants"].config(text=str(trades_gagnants))
        self.stats_labels["trades_perdants"].config(text=str(trades_perdants))
        self.stats_labels["taux_reussite"].config(text=f"{taux_reussite:.1f}%")
        self.stats_labels["profit_total"].config(text=f"{profit_total:,.2f} €")
        self.stats_labels["solde_final"].config(text=f"{solde_final:,.2f} €")
    
    def open_report(self):
        """Ouvre le rapport Excel"""
        if hasattr(self, 'report_path') and os.path.exists(self.report_path):
            try:
                os.startfile(self.report_path)  # Windows
            except AttributeError:
                try:
                    subprocess.run(['open', self.report_path])  # macOS
                except FileNotFoundError:
                    subprocess.run(['xdg-open', self.report_path])  # Linux
        else:
            messagebox.showwarning("Attention", "Aucun rapport disponible.")
    
    def open_reports_folder(self):
        """Ouvre le dossier des rapports"""
        reports_folder = "reports"
        if os.path.exists(reports_folder):
            try:
                os.startfile(reports_folder)  # Windows
            except AttributeError:
                try:
                    subprocess.run(['open', reports_folder])  # macOS
                except FileNotFoundError:
                    subprocess.run(['xdg-open', reports_folder])  # Linux
        else:
            messagebox.showwarning("Attention", "Le dossier des rapports n'existe pas.")
    
    def show_error(self, error_msg):
        """Affiche une erreur"""
        messagebox.showerror("Erreur", error_msg)
        self.status_label.config(text="❌ Erreur lors de l'analyse")
        self.analyze_btn.config(state='normal')
        self.select_files_btn.config(state='normal')
    
    def update_progress(self):
        """Met à jour la barre de progression"""
        if 'current_task' in self.task_status:
            progress = self.task_status['current_task']['progress']
            message = self.task_status['current_task']['message']
            
            self.progress_var.set(progress)
            self.status_label.config(text=message)
        
        # Continuer à mettre à jour toutes les 100ms
        self.root.after(100, self.update_progress)

def main():
    """Fonction principale"""
    root = tk.Tk()
    app = ModernTradingAnalyzerGUI(root)
    
    # Démarrer la mise à jour de la progression
    app.update_progress()
    
    # Lancer l'interface
    root.mainloop()

if __name__ == "__main__":
    main() 