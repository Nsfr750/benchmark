"""
Translations for the Benchmark application.
Contains all text strings in all supported languages.
"""

TRANSLATIONS = {
    'en': {
        "history": {
            "title": "Benchmark History",
            "filter": "Filter:",
            "filter_all": "All time",
            "filter_today": "Today",
            "filter_week": "Last 7 days",
            "filter_month": "Last 30 days",
            "filter_custom": "Custom range...",
            "column_date": "Date/Time",
            "column_pystones": "Pystones/s",
            "column_time": "Time (s)",
            "column_iterations": "Iterations",
            "column_cpu": "CPU",
            "column_system": "System",
            "results_count": "Showing {count} results",
            "compare": "Compare Selected",
            "delete": "Delete Selected",
            "delete_title": "Confirm Deletion",
            "delete_confirm": "Are you sure you want to delete the selected benchmark result?",
            "delete_success": "The benchmark result has been deleted.",
            "delete_error": "Failed to delete the benchmark result.",
            "deleted": "Deleted",
            "no_results": "No benchmark results found.",
            "export": "Export...",
            "import": "Import..."
        },
        "app": {
            "title": "Benchmark",
            "version": "Version",
            "ready": "Ready",
            "welcome": "Welcome to {app_name}",
            "start_benchmark": "Start Benchmark",
            "stop_benchmark": "Stop Benchmark",
            "iterations": "Iterations",
            "pystones_per_second": "Pystones/Second",
            "benchmark_results": "Benchmark Results",
            "time_elapsed": "Time Elapsed",
            "status_ready": "Ready",
            "status_running": "Running...",
            "status_completed": "Completed",
            "status_stopped": "Stopped",
            "starting_benchmark": "Starting benchmark...",
            "status_error": "Error"
        },
        "status": {
            "initializing": "Initializing...",
            "ready": "Ready",
            "running": "Running benchmark...",
            "completed": "Benchmark completed",
            "error": "Error occurred"
        },
        "help": {
            "title": "Help",
            "error_loading": "Could not load help documentation\n\nPlease visit the GitHub repository for documentation",
            "getting_started": "Getting Started",
            "welcome": "Welcome to Benchmark! This application allows you to benchmark your system's performance using the Pystone benchmark."
        },
        "benchmark_tests": {
            "title": "Benchmark Tests",
            "test_category": "Test Category",
            "status": "Status",
            "cpu": "CPU"
        },
        "messages": {
            "benchmark_started": "Benchmark started with {iterations} iterations",
            "benchmark_completed": "Benchmark completed in {time:.2f} seconds with {pystones:,.2f} pystones/second",
            "benchmark_stopped": "Benchmark stopped by user",
            "invalid_iterations": "Please enter a valid number of iterations"
        },
        "visualization": {
            "title": "Benchmark Results Visualization",
            "summary": "Summary",
            "overall_score": "Overall Score",
            "overall_score_desc": "Based on all benchmark results"
        },
        "about": {
            "title": "About",
            "description": "A Python implementation of the Pystone benchmark and other tests with a modern GUI interface.",
            "credits": "Credits",
            "connect": "Connect with me on GitHub"
        },
        "menu": {
            "file": "File",
            "exit": "Exit",
            "view": "View",
            "theme": "Theme"
        },
        "test": {
            "label": "Test",
            "pystone_test": "Pystone Benchmark",
            "pystone_tooltip": "Run Pystone benchmark test",
            "export_dialog": "Export Results"
        },
        "log_viewer": {
            "title": "Log Viewer",
            "refresh": "&Refresh",
            "clear": "&Clear Log",
            "save_as": "&Save As..."
        }
    },
    'it': {
        "history": {
            "title": "Cronologia Benchmark",
            "filter": "Filtra:",
            "filter_all": "Tutti",
            "filter_today": "Oggi",
            "filter_week": "Ultimi 7 giorni",
            "filter_month": "Ultimi 30 giorni",
            "filter_custom": "Intervallo personalizzato...",
            "column_date": "Data/Ora",
            "column_pystones": "Pystones/s",
            "column_time": "Tempo (s)",
            "column_iterations": "Iterazioni",
            "column_cpu": "CPU",
            "column_system": "Sistema",
            "results_count": "Mostrati {count} risultati",
            "compare": "Confronta Selezionati",
            "delete": "Elimina Selezionati",
            "delete_title": "Conferma Eliminazione",
            "delete_confirm": "Sei sicuro di voler eliminare il risultato selezionato?",
            "delete_success": "Il risultato del benchmark è stato eliminato.",
            "delete_error": "Impossibile eliminare il risultato del benchmark.",
            "deleted": "Eliminato",
            "no_results": "Nessun risultato del benchmark trovato.",
            "export": "Esporta...",
            "import": "Importa..."
        },
        "app": {
            "title": "Benchmark",
            "version": "Versione",
            "ready": "Pronto",
            "welcome": "Benvenuto in {app_name}",
            "start_benchmark": "Avvia Benchmark",
            "stop_benchmark": "Ferma Benchmark",
            "iterations": "Iterazioni",
            "pystones_per_second": "Pystones/Secondo",
            "benchmark_results": "Risultati Benchmark",
            "time_elapsed": "Tempo Trascorso",
            "status_ready": "Pronto",
            "status_running": "In esecuzione...",
            "status_completed": "Completato",
            "status_stopped": "Fermato",
            "starting_benchmark": "Avvio benchmark...",
            "status_error": "Errore"
        },
        "status": {
            "initializing": "Inizializzazione...",
            "ready": "Pronto",
            "running": "Esecuzione benchmark...",
            "completed": "Benchmark completato",
            "error": "Si è verificato un errore"
        },
        "help": {
            "title": "Aiuto",
            "error_loading": "Impossibile caricare la documentazione\n\nVisita il repository GitHub per la documentazione",
            "getting_started": "Per Iniziare",
            "welcome": "Benvenuto in Benchmark! Questa applicazione ti permette di misurare le prestazioni del tuo sistema utilizzando il benchmark Pystone."
        },
        "benchmark_tests": {
            "title": "Test di Benchmark",
            "test_category": "Categoria Test",
            "status": "Stato",
            "cpu": "CPU"
        },
        "messages": {
            "benchmark_started": "Benchmark avviato con {iterations} iterazioni",
            "benchmark_completed": "Benchmark completato in {time:.2f} secondi con {pystones:,.2f} pystones/secondo",
            "benchmark_stopped": "Benchmark interrotto dall'utente",
            "invalid_iterations": "Inserire un numero valido di iterazioni"
        },
        "visualization": {
            "title": "Visualizzazione Risultati Benchmark",
            "summary": "Riepilogo",
            "overall_score": "Punteggio Complessivo",
            "overall_score_desc": "Basato su tutti i risultati del benchmark"
        },
        "about": {
            "title": "Informazioni",
            "description": "Un'implementazione Python del benchmark Pystone e altri test con un'interfaccia grafica moderna.",
            "credits": "Crediti",
            "connect": "Connettiti con me su GitHub"
        },
        "menu": {
            "file": "File",
            "exit": "Esci",
            "view": "Visualizza",
            "theme": "Tema"
        },
        "test": {
            "label": "Test",
            "pystone_test": "Benchmark Pystone",
            "pystone_tooltip": "Esegui il test di benchmark Pystone",
            "export_dialog": "Esporta Risultati"
        },
        "log_viewer": {
            "title": "Visualizzatore Log",
            "refresh": "&Aggiorna",
            "clear": "P&ulisci Log",
            "save_as": "&Salva con nome..."
        }
    }
}

def get_translation(lang_code, key, default=None):
    """
    Get a translation for the given language code and key.
    
    Args:
        lang_code: Language code (e.g., 'en', 'it')
        key: Dot-separated key path (e.g., 'app.title')
        default: Default value to return if key not found
    
    Returns:
        The translated string or the default value if not found
    """
    if lang_code not in TRANSLATIONS:
        lang_code = 'en'  # Fallback to English
    
    parts = key.split('.')
    result = TRANSLATIONS[lang_code]
    
    try:
        for part in parts:
            result = result[part]
        return result
    except (KeyError, TypeError):
        return default if default is not None else key
