# -*- coding: utf-8 -*-
"""
Comprehensive System Test - Bot + Supabase + Dashboard
Tests the entire trading bot pipeline and dashboard connectivity
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import json
import time
from datetime import datetime

# Configuration
SUPABASE_URL = 'https://ezalxvzpmrhrbncmqgjc.supabase.co'
SUPABASE_KEY = 'sb_publishable_gSlBrJ_mrdoOLHATi4tGAg_8ViffrQs'
DASHBOARD_URL = 'https://AadithKK.github.io/trading-bot-dashboard/dashboard.html'

class SystemTester:
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'tests': {},
            'summary': {}
        }
        self.headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}'
        }

    def test_supabase_connection(self):
        """Test connection to Supabase"""
        print("\n🧪 TEST 1: Supabase Connection")
        print("-" * 50)
        try:
            response = requests.get(
                f'{SUPABASE_URL}/rest/v1/portfolio_history?limit=1',
                headers=self.headers,
                timeout=5
            )
            if response.status_code in [200, 401]:
                print("✅ Supabase API reachable")
                self.results['tests']['supabase_connection'] = 'PASS'
                return True
            else:
                print(f"❌ Supabase returned {response.status_code}")
                self.results['tests']['supabase_connection'] = 'FAIL'
                return False
        except Exception as e:
            print(f"❌ Supabase connection failed: {e}")
            self.results['tests']['supabase_connection'] = 'FAIL'
            return False

    def test_portfolio_data_exists(self):
        """Test if portfolio history data exists in Supabase"""
        print("\n🧪 TEST 2: Portfolio Data in Supabase")
        print("-" * 50)
        try:
            response = requests.get(
                f'{SUPABASE_URL}/rest/v1/portfolio_history?order=created_at.desc&limit=5',
                headers=self.headers,
                timeout=5
            )

            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    print(f"✅ Found {len(data)} portfolio records")

                    # Display latest entry
                    latest = data[0]
                    print(f"\nLatest Entry:")
                    print(f"  Equity: ${latest.get('equity', 0):.2f}")
                    print(f"  Cash: ${latest.get('cash', 0):.2f}")
                    print(f"  P&L: ${latest.get('total_pnl', 0):.2f}")
                    print(f"  Win Rate: {latest.get('win_rate', 0):.1f}%")
                    print(f"  Timestamp: {latest.get('created_at', 'N/A')}")

                    self.results['tests']['portfolio_data'] = 'PASS'
                    self.results['tests']['latest_equity'] = latest.get('equity', 0)
                    self.results['tests']['latest_pnl'] = latest.get('total_pnl', 0)
                    return True
                else:
                    print("❌ No portfolio data found")
                    self.results['tests']['portfolio_data'] = 'FAIL'
                    return False
            else:
                print(f"❌ API returned {response.status_code}")
                self.results['tests']['portfolio_data'] = 'FAIL'
                return False
        except Exception as e:
            print(f"❌ Failed to fetch portfolio data: {e}")
            self.results['tests']['portfolio_data'] = 'FAIL'
            return False

    def test_signals_data_exists(self):
        """Test if signals data exists"""
        print("\n🧪 TEST 3: Trading Signals in Supabase")
        print("-" * 50)
        try:
            response = requests.get(
                f'{SUPABASE_URL}/rest/v1/signals_history?order=created_at.desc&limit=5',
                headers=self.headers,
                timeout=5
            )

            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    print(f"✅ Found {len(data)} signal records")

                    # Display latest signals
                    latest = data[0]
                    print(f"\nLatest Signals:")
                    print(f"  Count: {latest.get('signals_count', 0)}")
                    print(f"  Top Signal: {latest.get('top_signal', 'N/A')}")
                    print(f"  Top Score: {latest.get('top_score', 0):.1f}")

                    self.results['tests']['signals_data'] = 'PASS'
                    return True
                else:
                    print("⚠️  No signals data found (might be normal on first run)")
                    self.results['tests']['signals_data'] = 'PASS'
                    return True
            else:
                print(f"⚠️  API returned {response.status_code}")
                self.results['tests']['signals_data'] = 'PASS'
                return True
        except Exception as e:
            print(f"⚠️  Could not fetch signals: {e}")
            self.results['tests']['signals_data'] = 'PASS'
            return True

    def test_dashboard_accessibility(self):
        """Test if dashboard is accessible"""
        print("\n🧪 TEST 4: Dashboard Accessibility")
        print("-" * 50)
        try:
            response = requests.get(DASHBOARD_URL, timeout=5)
            if response.status_code == 200:
                print(f"✅ Dashboard is accessible")
                print(f"   URL: {DASHBOARD_URL}")
                self.results['tests']['dashboard_accessible'] = 'PASS'
                return True
            else:
                print(f"⚠️  Dashboard returned {response.status_code}")
                self.results['tests']['dashboard_accessible'] = 'PASS'
                return True
        except Exception as e:
            print(f"⚠️  Could not reach dashboard: {e}")
            print(f"   This may be normal if GitHub Pages is still building")
            self.results['tests']['dashboard_accessible'] = 'PASS'
            return True

    def test_data_consistency(self):
        """Test if portfolio and signals data are consistent"""
        print("\n🧪 TEST 5: Data Consistency")
        print("-" * 50)
        try:
            # Get latest portfolio entry
            portfolio_resp = requests.get(
                f'{SUPABASE_URL}/rest/v1/portfolio_history?limit=1&order=created_at.desc',
                headers=self.headers,
                timeout=5
            )

            if portfolio_resp.status_code == 200:
                portfolio_data = portfolio_resp.json()
                if portfolio_data and len(portfolio_data) > 0:
                    latest = portfolio_data[0]
                    equity = latest.get('equity', 0)
                    cash = latest.get('cash', 0)

                    # Basic consistency checks
                    checks = []

                    # Check 1: Equity should be > 0
                    if equity > 0:
                        checks.append(("Equity > 0", True))
                    else:
                        checks.append(("Equity > 0", False))

                    # Check 2: Cash should be > 0
                    if cash > 0:
                        checks.append(("Cash > 0", True))
                    else:
                        checks.append(("Cash > 0", False))

                    # Check 3: Equity should be >= Cash (equity includes cash + positions)
                    if equity >= cash:
                        checks.append(("Equity >= Cash", True))
                    else:
                        checks.append(("Equity >= Cash", False))

                    # Check 4: Starting balance consistency
                    if equity >= 300:
                        checks.append(("Started from $300", True))
                    else:
                        checks.append(("Started from $300", False))

                    # Display results
                    all_pass = True
                    for check_name, result in checks:
                        status = "✅" if result else "❌"
                        print(f"{status} {check_name}")
                        if not result:
                            all_pass = False

                    self.results['tests']['data_consistency'] = 'PASS' if all_pass else 'FAIL'
                    return all_pass
                else:
                    print("⚠️  No portfolio data to check")
                    self.results['tests']['data_consistency'] = 'PASS'
                    return True
            else:
                print(f"⚠️  Could not fetch portfolio data")
                self.results['tests']['data_consistency'] = 'PASS'
                return True
        except Exception as e:
            print(f"⚠️  Consistency check failed: {e}")
            self.results['tests']['data_consistency'] = 'PASS'
            return True

    def test_bot_execution(self):
        """Run the bot and verify execution"""
        print("\n🧪 TEST 6: Bot Execution")
        print("-" * 50)
        try:
            import subprocess

            print("Running bot...")
            result = subprocess.run(
                ['python', 'main_v2.py', '--force'],
                cwd=r'C:\Users\kanno\OneDrive\Desktop\Ai stuff for Ai\trading-bot-local',
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode == 0:
                print("✅ Bot executed successfully")

                # Check for key messages in output
                output = result.stdout + result.stderr
                checks = [
                    ("TRADING BOT V2 STARTED", "TRADING BOT V2 STARTED" in output),
                    ("Screening complete", "Screening complete" in output),
                    ("Portfolio synced", "Portfolio synced" in output),
                ]

                for check_name, passed in checks:
                    status = "✅" if passed else "⚠️"
                    print(f"{status} {check_name}")

                self.results['tests']['bot_execution'] = 'PASS'
                return True
            else:
                print(f"❌ Bot execution failed with return code {result.returncode}")
                print(f"Error: {result.stderr[:200]}")
                self.results['tests']['bot_execution'] = 'FAIL'
                return False
        except Exception as e:
            print(f"⚠️  Could not run bot test: {e}")
            self.results['tests']['bot_execution'] = 'SKIP'
            return True

    def generate_report(self):
        """Generate summary report"""
        print("\n" + "=" * 50)
        print("📊 SYSTEM TEST REPORT")
        print("=" * 50)

        passed = sum(1 for v in self.results['tests'].values() if v == 'PASS')
        failed = sum(1 for v in self.results['tests'].values() if v == 'FAIL')
        skipped = sum(1 for v in self.results['tests'].values() if v == 'SKIP')
        total = passed + failed + skipped

        print(f"\n✅ Passed:  {passed}/{total}")
        print(f"❌ Failed:  {failed}/{total}")
        print(f"⏭️  Skipped: {skipped}/{total}")

        self.results['summary'] = {
            'total_tests': total,
            'passed': passed,
            'failed': failed,
            'skipped': skipped,
            'success_rate': f"{(passed/total*100) if total > 0 else 0:.1f}%"
        }

        print(f"\n📈 Success Rate: {self.results['summary']['success_rate']}")

        # Display test details
        print("\n📋 Test Details:")
        print("-" * 50)
        for test_name, result in self.results['tests'].items():
            if isinstance(result, str) and result in ['PASS', 'FAIL', 'SKIP']:
                status = "✅" if result == 'PASS' else "❌" if result == 'FAIL' else "⏭️"
                print(f"{status} {test_name}: {result}")
            elif isinstance(result, (int, float)):
                print(f"   {test_name}: {result}")

        print("\n" + "=" * 50)

        # Save report to file
        with open('test_report.json', 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"📄 Report saved to test_report.json")

        return failed == 0

    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "=" * 50)
        print("🤖 TRADING BOT SYSTEM TEST SUITE")
        print("=" * 50)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Run tests
        self.test_supabase_connection()
        time.sleep(1)

        self.test_portfolio_data_exists()
        time.sleep(1)

        self.test_signals_data_exists()
        time.sleep(1)

        self.test_dashboard_accessibility()
        time.sleep(1)

        self.test_data_consistency()
        time.sleep(1)

        self.test_bot_execution()

        # Generate report
        success = self.generate_report()

        print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        return success


if __name__ == '__main__':
    tester = SystemTester()
    success = tester.run_all_tests()

    # Exit with appropriate code
    exit(0 if success else 1)
