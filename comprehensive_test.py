#!/usr/bin/env python3
"""
Comprehensive validation test for all ULTRON Agent enhancement tools
"""

from tools.enhanced_nlp_tool import EnhancedNLPTool
from tools.mobile_web_interface_tool import MobileWebInterfaceTool
from tools.service_integration_tool import ServiceIntegrationTool
from tools.web_scraping_tool import WebScrapingTool
from tools.database_tool import DatabaseTool

def test_enhanced_nlp():
    """Test Enhanced NLP Tool"""
    print('1. Enhanced NLP Tool:')
    try:
        nlp = EnhancedNLPTool()
        result = nlp.execute('analyze text: Hello world, this is a test sentence.')
        success = 'words' in result.lower() or 'analysis' in result.lower()
        print('✅ NLP Analysis:', 'SUCCESS' if success else 'FAILED')
        return success
    except Exception as e:
        print('❌ NLP Analysis: FAILED -', str(e))
        return False

def test_mobile_web_interface():
    """Test Mobile Web Interface Tool"""
    print('\n2. Mobile Web Interface Tool:')
    try:
        web = MobileWebInterfaceTool()
        result = web.execute('start web interface')
        success = 'started' in result.lower() or 'running' in result.lower()
        print('✅ Web Interface:', 'SUCCESS' if success else 'FAILED')
        return success
    except Exception as e:
        print('❌ Web Interface: FAILED -', str(e))
        return False

def test_service_integration():
    """Test Service Integration Tool"""
    print('\n3. Service Integration Tool:')
    try:
        service = ServiceIntegrationTool()
        result = service.execute('make api call GET https://httpbin.org/json')
        success = '200' in result or 'json' in result.lower() or 'success' in result.lower()
        print('✅ API Call:', 'SUCCESS' if success else 'FAILED')
        return success
    except Exception as e:
        print('❌ API Call: FAILED -', str(e))
        return False

def test_web_scraping():
    """Test Web Scraping Tool"""
    print('\n4. Web Scraping Tool:')
    try:
        scraper = WebScrapingTool()
        result = scraper.execute('scrape website https://httpbin.org/html')
        success = 'html' in result.lower() or 'content' in result.lower() or 'scraped' in result.lower()
        print('✅ Web Scraping:', 'SUCCESS' if success else 'FAILED')
        return success
    except Exception as e:
        print('❌ Web Scraping: FAILED -', str(e))
        return False

def test_database_tool():
    """Test Database Tool"""
    print('\n5. Database Tool:')
    try:
        db = DatabaseTool()
        result = db.execute('store data table conversations {user_input: "test", ai_response: "ok"}')
        success = 'stored' in result.lower() or 'success' in result.lower()
        print('✅ Database Store:', 'SUCCESS' if success else 'FAILED')
        return success
    except Exception as e:
        print('❌ Database Store: FAILED -', str(e))
        return False

def main():
    print('=== ULTRON Agent Enhancement Tools Validation ===\n')

    results = []
    results.append(test_enhanced_nlp())
    results.append(test_mobile_web_interface())
    results.append(test_service_integration())
    results.append(test_web_scraping())
    results.append(test_database_tool())

    print(f'\n=== Validation Results: {sum(results)}/{len(results)} tools working ===')

    if all(results):
        print('🎉 All enhancement tools are fully functional!')
    else:
        print('⚠️  Some tools need attention.')

if __name__ == '__main__':
    main()
