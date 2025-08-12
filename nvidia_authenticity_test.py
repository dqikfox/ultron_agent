"""
NVIDIA Advice Verification Test
Checks if we're actually getting real, unique advice from NVIDIA models
"""

import asyncio
import json
import logging
from datetime import datetime
import time

from nvidia_nim_router import UltronNvidiaRouter

async def test_nvidia_model_authenticity():
    """Test if NVIDIA models are giving real, unique responses"""
    
    print("🔴 NVIDIA MODEL AUTHENTICITY TEST 🔴")
    print("=" * 60)
    print("Testing if NVIDIA models provide unique, real advice or just repeat the same responses")
    print("")
    
    router = UltronNvidiaRouter()
    
    # Test 1: Same query multiple times - should get different responses
    print("🧪 TEST 1: Response Variability Check")
    print("-" * 40)
    
    base_query = "Give me one specific improvement suggestion for ULTRON Agent accessibility"
    responses = []
    
    for i in range(3):
        print(f"Query {i+1}: {base_query}")
        
        try:
            response = await router.ask_nvidia_async(
                base_query,
                max_tokens=200,
                temperature=0.8  # Higher temperature for variability
            )
            
            responses.append(response)
            print(f"Response {i+1}: {response[:100]}...")
            print("")
            
            # Wait between requests
            await asyncio.sleep(2)
            
        except Exception as e:
            print(f"Error in query {i+1}: {e}")
            responses.append(f"ERROR: {e}")
    
    # Check for uniqueness
    unique_responses = len(set(responses))
    print(f"📊 Uniqueness Test Results:")
    print(f"   Total Responses: {len(responses)}")
    print(f"   Unique Responses: {unique_responses}")
    print(f"   Variability: {'✅ PASS' if unique_responses > 1 else '❌ FAIL - Identical responses'}")
    print("")
    
    # Test 2: Different specific questions - should get relevant answers
    print("🧪 TEST 2: Context-Specific Response Check")
    print("-" * 40)
    
    specific_queries = [
        "What's the best color contrast ratio for disabled users?",
        "How can I optimize Python memory usage for a 4GB system?", 
        "What voice recognition accuracy is considered good?",
        "Name one specific PyAutoGUI safety feature that should be added",
        "What's the ideal font size for visually impaired users?"
    ]
    
    context_responses = {}
    
    for query in specific_queries:
        print(f"Specific Query: {query}")
        
        try:
            response = await router.ask_nvidia_async(
                query,
                max_tokens=150,
                temperature=0.3
            )
            
            context_responses[query] = response
            print(f"Response: {response[:80]}...")
            
            # Check if response seems relevant to the question
            query_keywords = query.lower().split()
            response_lower = response.lower()
            
            relevant_matches = sum(1 for word in query_keywords if word in response_lower)
            relevance_score = relevant_matches / len(query_keywords)
            
            print(f"Relevance Score: {relevance_score:.2f} ({'✅ RELEVANT' if relevance_score > 0.2 else '❌ NOT RELEVANT'})")
            print("")
            
            await asyncio.sleep(2)
            
        except Exception as e:
            print(f"Error: {e}")
            context_responses[query] = f"ERROR: {e}"
            print("")
    
    # Test 3: Check if responses contain actual NVIDIA model characteristics
    print("🧪 TEST 3: Model Signature Check")
    print("-" * 40)
    
    signature_query = "Explain in detail how machine learning works, include technical terms"
    
    try:
        detailed_response = await router.ask_nvidia_async(
            signature_query,
            max_tokens=500,
            temperature=0.5
        )
        
        print(f"Detailed Response Preview: {detailed_response[:200]}...")
        
        # Check for AI model characteristics
        ai_indicators = [
            "neural network", "algorithm", "training", "model", "learning",
            "data", "parameters", "weights", "optimization", "gradient"
        ]
        
        found_indicators = [term for term in ai_indicators if term in detailed_response.lower()]
        
        print(f"AI Technical Terms Found: {len(found_indicators)}/10")
        print(f"Found Terms: {found_indicators[:5]}")
        print(f"Technical Depth: {'✅ AUTHENTIC' if len(found_indicators) >= 3 else '❌ SUSPICIOUS - Too simple'}")
        
    except Exception as e:
        print(f"Error in detailed query: {e}")
    
    print("")
    
    # Test 4: Check current model and API status
    print("🧪 TEST 4: API Status and Model Info")
    print("-" * 40)
    
    print(f"Current Model: {router.current_model}")
    print(f"Available Models: {list(router.models.keys())}")
    print(f"Request History Count: {len(router.request_history)}")
    
    if router.request_history:
        last_request = router.request_history[-1]
        print(f"Last Request Status: {last_request.get('status', 'Unknown')}")
        print(f"Last Response Length: {len(last_request.get('response', ''))}")
    
    # Final verdict
    print("\n" + "=" * 60)
    print("🔴 AUTHENTICITY VERDICT 🔴")
    print("=" * 60)
    
    authenticity_score = 0
    max_score = 4
    
    # Score based on tests
    if unique_responses > 1:
        authenticity_score += 1
        print("✅ Responses show variability")
    else:
        print("❌ Responses are identical (suspicious)")
    
    relevant_count = sum(1 for r in context_responses.values() if "ERROR" not in r and len(r) > 20)
    if relevant_count >= 3:
        authenticity_score += 1
        print("✅ Context-specific responses seem relevant")
    else:
        print("❌ Responses lack context relevance")
    
    if len(found_indicators) >= 3:
        authenticity_score += 1
        print("✅ Technical responses show AI model depth")
    else:
        print("❌ Technical responses too simple")
    
    if len(router.request_history) > 0:
        authenticity_score += 1
        print("✅ API calls are being made")
    else:
        print("❌ No API call history found")
    
    final_score = (authenticity_score / max_score) * 100
    
    print(f"\n🎯 AUTHENTICITY SCORE: {final_score:.1f}%")
    
    if final_score >= 75:
        print("🎉 VERDICT: AUTHENTIC - NVIDIA models are providing real, unique advice")
    elif final_score >= 50:
        print("⚠️  VERDICT: MIXED - Some authenticity concerns, needs investigation")
    else:
        print("❌ VERDICT: SUSPICIOUS - Responses may be pre-generated or fake")
    
    return {
        "authenticity_score": final_score,
        "unique_responses": unique_responses,
        "context_responses": len(context_responses),
        "technical_depth": len(found_indicators),
        "api_calls": len(router.request_history)
    }

async def test_improvement_system_freshness():
    """Test if the improvement advisory system generates fresh content"""
    
    print("\n" + "=" * 60)
    print("🔄 IMPROVEMENT SYSTEM FRESHNESS TEST")
    print("=" * 60)
    
    from ultron_project_advisor import UltronProjectAdvisor
    
    advisor = UltronProjectAdvisor()
    
    # Test different improvement areas
    areas_to_test = [
        "accessibility_enhancements",
        "voice_recognition_accuracy", 
        "gui_responsiveness"
    ]
    
    fresh_suggestions = {}
    
    for area in areas_to_test:
        print(f"\n🎯 Testing {area.replace('_', ' ').title()}")
        print("-" * 30)
        
        try:
            # Get suggestion using the advisor's method
            suggestion = await advisor.query_nvidia_for_advice(area, "llama")
            
            fresh_suggestions[area] = suggestion
            
            if "error" not in suggestion:
                response = suggestion.get("response", "")
                print(f"Response Length: {len(response)} characters")
                print(f"Preview: {response[:150]}...")
                
                # Check if it's actually fresh content
                if len(response) > 50:
                    print("✅ Substantial content received")
                else:
                    print("❌ Response too short or empty")
            else:
                print(f"❌ Error: {suggestion.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Exception testing {area}: {e}")
            fresh_suggestions[area] = {"error": str(e)}
    
    # Analysis
    successful_suggestions = sum(1 for s in fresh_suggestions.values() if "error" not in s and len(s.get("response", "")) > 50)
    
    print(f"\n📊 FRESHNESS TEST RESULTS:")
    print(f"   Areas Tested: {len(areas_to_test)}")
    print(f"   Successful Responses: {successful_suggestions}")
    print(f"   Success Rate: {(successful_suggestions/len(areas_to_test)*100):.1f}%")
    
    if successful_suggestions >= 2:
        print("✅ FRESH CONTENT: System is generating new suggestions")
    else:
        print("❌ STALE CONTENT: System may be using pre-generated responses")
    
    return fresh_suggestions

async def main():
    """Run complete authenticity and freshness test"""
    
    print("🔴 COMPREHENSIVE NVIDIA ADVICE SYSTEM VERIFICATION 🔴")
    print("=" * 70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Testing if NVIDIA implementation provides real, unique advice")
    print("")
    
    try:
        # Test 1: NVIDIA Model Authenticity
        auth_results = await test_nvidia_model_authenticity()
        
        # Test 2: Improvement System Freshness
        fresh_results = await test_improvement_system_freshness()
        
        # Final Summary
        print("\n" + "=" * 70)
        print("🎉 COMPLETE VERIFICATION RESULTS 🎉")
        print("=" * 70)
        
        overall_score = auth_results["authenticity_score"]
        
        print(f"🔍 Authenticity Score: {overall_score:.1f}%")
        print(f"🔄 Fresh Content: {'✅ YES' if len([r for r in fresh_results.values() if 'error' not in r]) >= 2 else '❌ NO'}")
        print(f"📊 API Connectivity: {'✅ WORKING' if auth_results['api_calls'] > 0 else '❌ FAILED'}")
        print(f"🎯 Response Variety: {'✅ VARIED' if auth_results['unique_responses'] > 1 else '❌ REPETITIVE'}")
        
        if overall_score >= 75:
            print("\n🎉 CONCLUSION: NVIDIA advice implementation is AUTHENTIC and working correctly!")
            print("   The system is providing real, unique improvements from NVIDIA models.")
        else:
            print("\n❌ CONCLUSION: NVIDIA advice implementation has AUTHENTICITY ISSUES!")
            print("   The system may be using pre-generated or fake responses.")
            print("   Recommend investigating the API connection and response generation.")
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR in verification: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
