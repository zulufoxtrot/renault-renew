#!/usr/bin/env python3
"""
Command-line interface for Renault Scraper
"""

import argparse
import sys
from src import config
from src.scraper import RenaultScraper
from src.reports import HTMLReportGenerator
from src.database import Database


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Renault Renew Scraper - Price tracking and vehicle monitoring'
    )

    parser.add_argument(
        '--db',
        type=str,
        default=config.DB_PATH,
        help=f'Database path (default: {config.DB_PATH})'
    )

    parser.add_argument(
        '--csv',
        action='store_true',
        help='Generate CSV report in addition to HTML'
    )

    parser.add_argument(
        '--no-db',
        action='store_true',
        help='Run scraper without saving to database'
    )

    parser.add_argument(
        '--report',
        type=str,
        default=config.REPORT_OUTPUT_FILE,
        help=f'Output HTML report file (default: {config.REPORT_OUTPUT_FILE})'
    )

    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show database statistics and exit'
    )

    args = parser.parse_args()

    # Show stats and exit
    if args.stats:
        try:
            db = Database(args.db)
            stats = db.get_statistics()
            db.close()

            print("\n📊 Database Statistics:")
            print(f"   Total Vehicles: {stats['total_vehicles']}")
            print(f"   Available Now: {stats['available_vehicles']}")
            print(f"   New (24h): {stats['new_vehicles_24h']}")
            print(f"   Price Tracked: {stats['vehicles_with_price_history']}")
            print()
            return 0
        except Exception as e:
            print(f"❌ Error: {e}")
            return 1

    # Run scraper
    try:
        print("\n🚗 Renault Scraper CLI")
        print("=" * 50)

        scraper = RenaultScraper(
            use_database=not args.no_db,
            db_path=args.db if not args.no_db else None
        )

        scraper.run()

        # Generate reports
        if not args.no_db:
            db = Database(args.db)

            # HTML Report
            print(f"\n📊 Generating HTML Report...")
            report_gen = HTMLReportGenerator(db)
            report_file = report_gen.generate_report(args.report)
            print(f"✅ Report saved: {report_file}")

            # Show stats
            stats = db.get_statistics()
            print(f"\n📈 Statistics:")
            print(f"   Total Vehicles: {stats['total_vehicles']}")
            print(f"   Available Now: {stats['available_vehicles']}")
            print(f"   New (24h): {stats['new_vehicles_24h']}")
            print(f"   Price Tracked: {stats['vehicles_with_price_history']}")

            db.close()

        print("\n✅ Scraping completed successfully!")
        return 0

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
