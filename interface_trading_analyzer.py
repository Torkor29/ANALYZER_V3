#!/usr/bin/env python3
"""
Interface graphique pour l'Analyseur de Trading Unifié
Permet de sélectionner plusieurs fichiers Excel et générer des rapports
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
from trading_analyzer_unified import TradingAnalyzer

class TradingAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🚀 Trading Analyzer Pro")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # Variables
        self.selected_files = []
        self.analyzer = TradingAnalyzer(solde_initial=10000)
        self.task_status = {'current_task': {'progress': 0, 'message': 'En attente...'}}
        
        # Création de l'interface
        self.create_widgets()
        
        # Centrer la fenêtre
        self.center_window()
    
    def center_window(self):
        """Centre la fenêtre sur l'écran"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """Crée tous les widgets de l'interface"""
        
        # Titre principal
        title_frame = tk.Frame(self.root, bg='#2c3e50', height=60)
        title_frame.pack(fill='x', padx=10, pady=10)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame, text="🚀 Trading Analyzer Pro", 
                              font=('Arial', 20, 'bold'), 
                              fg='white', bg='#2c3e50')
        title_label.pack(expand=True)
        
        # Frame principal
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Section 1: Sélection des fichiers
        self.create_file_selection_section(main_frame)
        
        # Section 2: Configuration
        self.create_configuration_section(main_frame)
        
        # Section 3: Progression
        self.create_progress_section(main_frame)
        
        # Section 4: Boutons d'action
        self.create_action_buttons(main_frame)
        
        # Section 5: Statut et résultats
        self.create_status_section(main_frame)
    
    def create_file_selection_section(self, parent):
        """Crée la section de sélection des fichiers"""
        file_frame = tk.LabelFrame(parent, text="📁 Sélection des fichiers Excel", 
                                  font=('Arial', 12, 'bold'), bg='#f0f0f0')
        file_frame.pack(fill='x', pady=10)
        
        # Boutons de sélection
        button_frame = tk.Frame(file_frame, bg='#f0f0f0')
        button_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Button(button_frame, text="📂 Ajouter des fichiers", 
                 command=self.add_files, bg='#3498db', fg='white',
                 font=('Arial', 10, 'bold')).pack(side='left', padx=5)
        
        tk.Button(button_frame, text="🗑️ Vider la liste", 
                 command=self.clear_files, bg='#e74c3c', fg='white',
                 font=('Arial', 10, 'bold')).pack(side='left', padx=5)
        
        # Liste des fichiers
        list_frame = tk.Frame(file_frame, bg='#f0f0f0')
        list_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Scrollbar pour la liste
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side='right', fill='y')
        
        # Listbox pour afficher les fichiers
        self.file_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set,
                                      font=('Arial', 9), bg='white', height=6)
        self.file_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.file_listbox.yview)
        
        # Label pour le nombre de fichiers
        self.file_count_label = tk.Label(file_frame, text="Aucun fichier sélectionné", 
                                        font=('Arial', 9), bg='#f0f0f0', fg='#666')
        self.file_count_label.pack(pady=5)
    
    def create_configuration_section(self, parent):
        """Crée la section de configuration"""
        config_frame = tk.LabelFrame(parent, text="⚙️ Configuration", 
                                    font=('Arial', 12, 'bold'), bg='#f0f0f0')
        config_frame.pack(fill='x', pady=10)
        
        # Solde initial
        balance_frame = tk.Frame(config_frame, bg='#f0f0f0')
        balance_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(balance_frame, text="💰 Solde initial (€):", 
                font=('Arial', 10), bg='#f0f0f0').pack(side='left')
        
        self.balance_var = tk.StringVar(value="10000")
        self.balance_entry = tk.Entry(balance_frame, textvariable=self.balance_var, 
                                     font=('Arial', 10), width=15)
        self.balance_entry.pack(side='left', padx=10)
        
        # Type d'analyse
        analysis_frame = tk.Frame(config_frame, bg='#f0f0f0')
        analysis_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(analysis_frame, text="📊 Type d'analyse:", 
                font=('Arial', 10), bg='#f0f0f0').pack(side='left')
        
        self.analysis_var = tk.StringVar(value="tous")
        analysis_combo = ttk.Combobox(analysis_frame, textvariable=self.analysis_var,
                                     values=["tous", "forex", "autres"], 
                                     state="readonly", width=15)
        analysis_combo.pack(side='left', padx=10)
        
        # Tooltip pour expliquer les options
        tk.Label(analysis_frame, text="💡 'tous' = Forex + autres, 'forex' = uniquement Forex, 'autres' = métaux, indices, crypto, etc.",
                font=('Arial', 8), bg='#f0f0f0', fg='#666').pack(side='left', padx=10)
    
    def create_progress_section(self, parent):
        """Crée la section de progression"""
        progress_frame = tk.LabelFrame(parent, text="📈 Progression", 
                                      font=('Arial', 12, 'bold'), bg='#f0f0f0')
        progress_frame.pack(fill='x', pady=10)
        
        # Barre de progression
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var,
                                           maximum=100, length=400)
        self.progress_bar.pack(pady=10)
        
        # Label de statut
        self.status_label = tk.Label(progress_frame, text="En attente...", 
                                    font=('Arial', 10), bg='#f0f0f0')
        self.status_label.pack(pady=5)
    
    def create_action_buttons(self, parent):
        """Crée les boutons d'action"""
        button_frame = tk.Frame(parent, bg='#f0f0f0')
        button_frame.pack(fill='x', pady=10)
        
        # Bouton de lancement
        self.launch_button = tk.Button(button_frame, text="🚀 Lancer l'analyse", 
                                      command=self.launch_analysis, 
                                      bg='#27ae60', fg='white',
                                      font=('Arial', 12, 'bold'), height=2)
        self.launch_button.pack(side='left', expand=True, padx=5)
        
        # Bouton pour ouvrir le rapport
        self.open_report_button = tk.Button(button_frame, text="📊 Ouvrir le rapport", 
                                           command=self.open_report, 
                                           bg='#f39c12', fg='white',
                                           font=('Arial', 12, 'bold'), height=2)
        self.open_report_button.pack(side='left', expand=True, padx=5)
        
        # Bouton pour ouvrir le dossier
        self.open_folder_button = tk.Button(button_frame, text="📁 Ouvrir le dossier", 
                                           command=self.open_folder, 
                                           bg='#9b59b6', fg='white',
                                           font=('Arial', 12, 'bold'), height=2)
        self.open_folder_button.pack(side='left', expand=True, padx=5)
        
        # Désactiver les boutons au début
        self.open_report_button.config(state='disabled')
        self.open_folder_button.config(state='disabled')
    
    def create_status_section(self, parent):
        """Crée la section de statut et résultats"""
        status_frame = tk.LabelFrame(parent, text="📋 Statut et résultats", 
                                    font=('Arial', 12, 'bold'), bg='#f0f0f0')
        status_frame.pack(fill='both', expand=True, pady=10)
        
        # Zone de texte pour les logs
        self.log_text = tk.Text(status_frame, height=8, font=('Consolas', 9),
                               bg='#2c3e50', fg='white', wrap='word')
        self.log_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Scrollbar pour les logs
        log_scrollbar = tk.Scrollbar(self.log_text)
        log_scrollbar.pack(side='right', fill='y')
        self.log_text.config(yscrollcommand=log_scrollbar.set)
        log_scrollbar.config(command=self.log_text.yview)
        
        # Variables pour stocker les résultats
        self.last_report_path = None
        self.reports_folder = None
    
    def add_files(self):
        """Ajoute des fichiers à la liste"""
        files = filedialog.askopenfilenames(
            title="Sélectionner les fichiers Excel",
            filetypes=[("Fichiers Excel", "*.xlsx *.xls"), ("Tous les fichiers", "*.*")]
        )
        
        for file in files:
            if file not in self.selected_files:
                self.selected_files.append(file)
                self.file_listbox.insert(tk.END, os.path.basename(file))
        
        self.update_file_count()
        self.log_message(f"✅ {len(files)} fichier(s) ajouté(s)")
    
    def clear_files(self):
        """Vide la liste des fichiers"""
        self.selected_files.clear()
        self.file_listbox.delete(0, tk.END)
        self.update_file_count()
        self.log_message("🗑️ Liste des fichiers vidée")
    
    def update_file_count(self):
        """Met à jour le compteur de fichiers"""
        count = len(self.selected_files)
        if count == 0:
            self.file_count_label.config(text="Aucun fichier sélectionné")
        elif count == 1:
            self.file_count_label.config(text="1 fichier sélectionné")
        else:
            self.file_count_label.config(text=f"{count} fichiers sélectionnés")
    
    def log_message(self, message):
        """Ajoute un message au log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def launch_analysis(self):
        """Lance l'analyse dans un thread séparé"""
        if not self.selected_files:
            messagebox.showwarning("Attention", "Veuillez sélectionner au moins un fichier Excel.")
            return
        
        try:
            # Mettre à jour le solde initial
            solde_initial = float(self.balance_var.get())
            self.analyzer.solde_initial = solde_initial
        except ValueError:
            messagebox.showerror("Erreur", "Le solde initial doit être un nombre valide.")
            return
        
        # Désactiver le bouton de lancement
        self.launch_button.config(state='disabled')
        
        # Lancer l'analyse dans un thread séparé
        thread = threading.Thread(target=self.run_analysis)
        thread.daemon = True
        thread.start()
    
    def run_analysis(self):
        """Exécute l'analyse (dans un thread séparé)"""
        try:
            self.log_message("🚀 Démarrage de l'analyse...")
            
            # Créer le dossier de rapports
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.reports_folder = os.path.join(os.getcwd(), "reports")
            os.makedirs(self.reports_folder, exist_ok=True)
            
            # Récupérer le type d'analyse
            analysis_type = self.analysis_var.get()
            if analysis_type == "tous":
                filter_type = None
            elif analysis_type == "forex":
                filter_type = "forex"
            else:  # "autres"
                filter_type = "autres"
            
            # Mettre à jour le statut
            self.task_status['current_task']['progress'] = 0
            self.task_status['current_task']['message'] = 'Démarrage...'
            
            # Lancer l'analyse
            df_result = self.analyzer.process_files(
                self.selected_files, 
                'current_task', 
                self.task_status, 
                filter_type
            )
            
            if df_result is not None:
                self.log_message(f"✅ Analyse terminée: {len(df_result)} trades traités")
                
                # Créer le rapport Excel
                self.log_message("📊 Génération du rapport Excel...")
                self.last_report_path = self.analyzer.create_excel_report(
                    df_result, 
                    self.reports_folder, 
                    timestamp, 
                    filter_type
                )
                
                self.log_message(f"✅ Rapport généré: {os.path.basename(self.last_report_path)}")
                
                # Activer les boutons
                self.root.after(0, self.enable_result_buttons)
                
            else:
                self.log_message("❌ Aucun résultat obtenu")
                
        except Exception as e:
            self.log_message(f"❌ Erreur: {str(e)}")
            messagebox.showerror("Erreur", f"Une erreur s'est produite:\n{str(e)}")
        
        finally:
            # Réactiver le bouton de lancement
            self.root.after(0, lambda: self.launch_button.config(state='normal'))
    
    def enable_result_buttons(self):
        """Active les boutons de résultats"""
        self.open_report_button.config(state='normal')
        self.open_folder_button.config(state='normal')
    
    def open_report(self):
        """Ouvre le rapport Excel"""
        if self.last_report_path and os.path.exists(self.last_report_path):
            try:
                os.startfile(self.last_report_path)  # Windows
            except:
                try:
                    subprocess.run(['open', self.last_report_path])  # macOS
                except:
                    subprocess.run(['xdg-open', self.last_report_path])  # Linux
            self.log_message("📊 Ouverture du rapport Excel...")
        else:
            messagebox.showwarning("Attention", "Aucun rapport disponible.")
    
    def open_folder(self):
        """Ouvre le dossier des rapports"""
        if self.reports_folder and os.path.exists(self.reports_folder):
            try:
                os.startfile(self.reports_folder)  # Windows
            except:
                try:
                    subprocess.run(['open', self.reports_folder])  # macOS
                except:
                    subprocess.run(['xdg-open', self.reports_folder])  # Linux
            self.log_message("📁 Ouverture du dossier des rapports...")
        else:
            messagebox.showwarning("Attention", "Dossier des rapports non trouvé.")
    
    def update_progress(self):
        """Met à jour la barre de progression"""
        progress = self.task_status['current_task']['progress']
        message = self.task_status['current_task']['message']
        
        self.progress_var.set(progress)
        self.status_label.config(text=message)
        
        # Programmer la prochaine mise à jour
        self.root.after(100, self.update_progress)

def main():
    """Fonction principale"""
    root = tk.Tk()
    app = TradingAnalyzerGUI(root)
    
    # Démarrer la mise à jour de la progression
    app.update_progress()
    
    # Lancer l'interface
    root.mainloop()

if __name__ == "__main__":
    main() 