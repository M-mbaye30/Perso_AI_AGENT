"""
Point d'entrée principal de l'agent de veille technologique
"""
import argparse
import sys
from agent import run_tech_watch_cycle, run_targeted_search, monitor_keywords
from config import NLP_KEYWORDS

def main():
    parser = argparse.ArgumentParser(
        description="Agent de veille technologique NLP"
    )
    
    parser.add_argument(
        '--mode', 
        choices=['cycle', 'search', 'monitor'],
        default='cycle',
        help='Mode d\'exécution'
    )
    
    parser.add_argument(
        '--query',
        type=str,
        help='Requête pour recherche ciblée'
    )
    
    parser.add_argument(
        '--keywords',
        nargs='+',
        help='Mots-clés personnalisés'
    )
    
    parser.add_argument(
        '--max-results',
        type=int,
        default=10,
        help='Nombre maximum de résultats'
    )
    
    parser.add_argument(
        '--interval',
        type=int,
        default=3600,
        help='Intervalle de surveillance (secondes)'
    )
    
    args = parser.parse_args()
    
    try:
        if args.mode == 'cycle':
            print("🚀 Lancement du cycle complet de veille")
            keywords = args.keywords or NLP_KEYWORDS
            report = run_tech_watch_cycle(keywords)
            
            if report:
                print(f"✅ Rapport généré : {report['metadata']['report_id']}")
                print(f"📊 Documents analysés : {report['summary']['total_documents_analyzed']}")
                print(f"🎯 Documents pertinents : {report['summary']['relevant_documents']}")
            else:
                print("❌ Erreur lors de la génération du rapport")
        
        elif args.mode == 'search':
            if not args.query:
                print("❌ Erreur : --query requis pour le mode search")
                sys.exit(1)
            
            print(f"🎯 Recherche ciblée : {args.query}")
            results = run_targeted_search(args.query, args.max_results)
            
            if 'error' in results:
                print(f"❌ {results['error']}")
            else:
                print(f"✅ {results['analyzed_count']} documents analysés")
        
        elif args.mode == 'monitor':
            keywords = args.keywords or NLP_KEYWORDS
            print(f"📡 Surveillance continue de {len(keywords)} mots-clés")
            print("Appuyez sur Ctrl+C pour arrêter")
            
            monitor_keywords(keywords, args.interval)
    
    except KeyboardInterrupt:
        print("\n👋 Arrêt de l'agent")
    except Exception as e:
        print(f"❌ Erreur : {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
