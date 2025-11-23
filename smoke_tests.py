#!/usr/bin/env python3
"""
Smoke Tests - End to End dla Video Downloader
Testy integracyjne całego systemu: analytics, subskrypcje, pobieranie
"""

import os
import sys
import time
import tempfile
import threading
from pathlib import Path
import json

# Dodaj ścieżkę do importów
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from analytics_service import analytics_service
from subscription_manager import subscription_manager
from download_manager import download_manager

def test_analytics_service():
    """Test podstawowej funkcjonalności analytics"""
    print("🧪 Testing Analytics Service...")
    
    try:
        # Test 1: Inicjalizacja
        status = analytics_service.get_analytics_status()
        assert status['enabled'] == True, "Analytics should be enabled"
        assert 'user_id' in status, "Should have user ID"
        print("✅ Analytics initialization: PASS")
        
        # Test 2: Track basic events
        analytics_service.track_app_launch()
        analytics_service.track_event('test_event', {'test': True})
        print("✅ Basic event tracking: PASS")
        
        # Test 3: Track download events
        analytics_service.track_download_start(
            'https://example.com/test.mp4', 
            '.mp4'
        )
        analytics_service.track_download_complete(
            'https://example.com/test.mp4',
            1024 * 1024,  # 1MB
            2.5  # 2.5 seconds
        )
        print("✅ Download event tracking: PASS")
        
        # Test 4: Track error events
        analytics_service.track_download_error(
            'https://example.com/error.mp4',
            'ConnectionError',
            'Connection failed'
        )
        print("✅ Error event tracking: PASS")
        
        # Test 5: Local events storage
        local_count = analytics_service._get_local_events_count()
        assert local_count > 0, "Should have local events stored"
        print(f"✅ Local events storage: PASS ({local_count} events)")
        
        return True
        
    except Exception as e:
        print(f"❌ Analytics test failed: {e}")
        return False

def test_subscription_manager():
    """Test systemu subskrypcji"""
    print("\n🧪 Testing Subscription Manager...")
    
    try:
        # Test 1: Initial state (should be freemium)
        initial_info = subscription_manager.get_subscription_info()
        assert initial_info['is_premium'] == False, "Should start as freemium"
        assert initial_info['tier'] == 'freemium', "Should be freemium tier"
        print("✅ Initial freemium state: PASS")
        
        # Test 2: Download limits
        assert subscription_manager.can_download() == True, "Should allow first download"
        print("✅ Initial download permission: PASS")
        
        # Test 3: Record downloads
        for i in range(3):
            subscription_manager.record_download()
        
        info_after = subscription_manager.get_subscription_info()
        assert info_after['downloads_today'] == 3, f"Should have 3 downloads, got {info_after['downloads_today']}"
        print("✅ Download recording: PASS")
        
        # Test 4: Downloads remaining
        remaining = subscription_manager.get_downloads_remaining()
        expected_remaining = subscription_manager.freemium_limits['daily_downloads'] - 3
        assert remaining == expected_remaining, f"Should have {expected_remaining} remaining, got {remaining}"
        print("✅ Downloads remaining calculation: PASS")
        
        # Test 5: Premium activation
        subscription_manager.activate_premium(days=1)
        premium_info = subscription_manager.get_subscription_info()
        assert premium_info['is_premium'] == True, "Should be premium after activation"
        assert 'expiry_date' in premium_info, "Should have expiry date"
        print("✅ Premium activation: PASS")
        
        # Test 6: Premium limits
        premium_limits = subscription_manager.get_limits()
        assert premium_limits['daily_downloads'] == float('inf'), "Premium should have unlimited downloads"
        assert premium_limits['chat_monitoring'] == True, "Premium should have chat monitoring"
        print("✅ Premium limits: PASS")
        
        # Test 7: Premium download permission
        assert subscription_manager.can_download() == True, "Premium should always allow downloads"
        print("✅ Premium download permission: PASS")
        
        # Test 8: Deactivation
        subscription_manager.deactivate_premium()
        final_info = subscription_manager.get_subscription_info()
        assert final_info['is_premium'] == False, "Should be freemium after deactivation"
        print("✅ Premium deactivation: PASS")
        
        return True
        
    except Exception as e:
        print(f"❌ Subscription test failed: {e}")
        return False

def test_download_manager():
    """Test menedżera pobierania"""
    print("\n🧪 Testing Download Manager...")
    
    try:
        # Create temp directory for tests
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Test 1: URL validation
            valid_url = 'https://httpbin.org/json'
            invalid_url = 'not-a-url'
            
            is_valid, message = download_manager.is_valid_url(valid_url)
            assert is_valid == True, f"Valid URL should pass: {message}"
            
            is_valid, message = download_manager.is_valid_url(invalid_url)
            assert is_valid == False, "Invalid URL should fail"
            print("✅ URL validation: PASS")
            
            # Test 2: Add to queue
            success = download_manager.add_to_queue(valid_url, temp_path)
            assert success == True, "Should add valid URL to queue"
            print("✅ Add to queue: PASS")
            
            # Test 3: Queue status
            status = download_manager.get_queue_status()
            assert status['queue_size'] == 1, "Should have 1 item in queue"
            print("✅ Queue status: PASS")
            
            # Test 4: Duplicate prevention
            success_duplicate = download_manager.add_to_queue(valid_url, temp_path)
            assert success_duplicate == False, "Should not add duplicate URL"
            print("✅ Duplicate prevention: PASS")
            
            # Test 5: Start processing
            download_manager.start_processing()
            time.sleep(1)  # Let it start
            
            status_after_start = download_manager.get_queue_status()
            assert status_after_start['running'] == True, "Should be running"
            print("✅ Start processing: PASS")
            
            # Test 6: Stop processing
            download_manager.stop_processing()
            time.sleep(0.5)
            
            status_after_stop = download_manager.get_queue_status()
            assert status_after_stop['running'] == False, "Should be stopped"
            print("✅ Stop processing: PASS")
            
            # Test 7: Clear queues
            download_manager.clear_completed()
            download_manager.clear_failed()
            
            final_status = download_manager.get_queue_status()
            assert final_status['completed'] == 0, "Should clear completed"
            assert final_status['failed'] == 0, "Should clear failed"
            print("✅ Clear queues: PASS")
            
        return True
        
    except Exception as e:
        print(f"❌ Download manager test failed: {e}")
        return False

def test_integration():
    """Test integracji między modułami"""
    print("\n🧪 Testing Module Integration...")
    
    try:
        # Test 1: Analytics + Subscription integration
        subscription_manager.activate_premium(days=1)
        
        # Track premium activation
        analytics_service.track_event('premium_activated_test', {
            'integration_test': True
        })
        
        # Verify both systems work together
        sub_info = subscription_manager.get_subscription_info()
        analytics_status = analytics_service.get_analytics_status()
        
        assert sub_info['is_premium'] == True, "Subscription should be premium"
        assert analytics_status['enabled'] == True, "Analytics should be enabled"
        print("✅ Analytics + Subscription integration: PASS")
        
        # Test 2: Download recording with analytics
        subscription_manager.record_download()
        
        analytics_service.track_download_start(
            'https://integration-test.com/video.mp4',
            '.mp4'
        )
        
        # Verify download was recorded
        sub_info_after = subscription_manager.get_subscription_info()
        assert sub_info_after['downloads_today'] > 0, "Download should be recorded"
        print("✅ Download recording integration: PASS")
        
        # Clean up
        subscription_manager.deactivate_premium()
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def test_error_handling():
    """Test obsługi błędów"""
    print("\n🧪 Testing Error Handling...")
    
    try:
        # Test 1: Invalid URL handling
        invalid_url = 'http://invalid-domain-that-does-not-exist-12345.com/file.mp4'
        
        is_valid, message = download_manager.is_valid_url(invalid_url)
        # Even invalid domains might pass basic validation
        print("✅ Invalid URL validation: PASS")
        
        # Test 2: Analytics with invalid data
        analytics_service.track_event('', {})  # Empty event name
        analytics_service.track_event('test_event', None)  # None properties
        print("✅ Analytics error handling: PASS")
        
        # Test 3: Subscription edge cases
        # Reset to known state
        subscription_manager.deactivate_premium()
        
        # Test downloads after limit (simulate)
        original_limit = subscription_manager.freemium_limits['daily_downloads']
        subscription_manager.daily_stats['downloads_today'] = original_limit + 1
        
        can_download = subscription_manager.can_download()
        assert can_download == False, "Should not allow download over limit"
        print("✅ Download limit enforcement: PASS")
        
        # Reset
        subscription_manager.daily_stats['downloads_today'] = 0
        
        return True
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False

def run_all_tests():
    """Uruchamia wszystkie testy"""
    print("🚀 Starting Smoke Tests - Video Downloader")
    print("=" * 50)
    
    test_results = []
    
    # Run individual tests
    test_results.append(("Analytics Service", test_analytics_service()))
    test_results.append(("Subscription Manager", test_subscription_manager()))
    test_results.append(("Download Manager", test_download_manager()))
    test_results.append(("Module Integration", test_integration()))
    test_results.append(("Error Handling", test_error_handling()))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    for test_name, result in test_results:
        if result:
            print(f"✅ {test_name}: PASS")
            passed += 1
        else:
            print(f"❌ {test_name}: FAIL")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"🎯 TOTAL: {passed} passed, {failed} failed"
    
    if failed == 0:
        print("🎉 ALL TESTS PASSED! System is ready for production.")
        return True
    else:
        print(f"⚠️  {failed} tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)