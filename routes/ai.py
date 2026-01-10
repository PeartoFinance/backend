"""
AI API Routes
Chat, analyze, and tool execution endpoints
"""
import re
import asyncio
from flask import Blueprint, jsonify, request
from datetime import datetime

ai_bp = Blueprint('ai', __name__)


@ai_bp.route('/chat', methods=['POST'])
def chat():
    """Basic chat endpoint"""
    from services.ai_service import ai_service
    
    data = request.get_json() or {}
    message = data.get('message', '')
    context = data.get('context', {})
    
    if not message:
        return jsonify({'error': 'Message is required'}), 400
    
    # Run async function
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(ai_service.chat(message, context))
        return jsonify({
            'success': result.get('success', False),
            'response': result.get('response', ''),
            'provider': result.get('provider', 'unknown'),
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        loop.close()


@ai_bp.route('/chat-with-tools', methods=['POST'])
def chat_with_tools():
    """Chat endpoint with tool execution"""
    from services.ai_service import ai_service
    from services.ai_tools import execute_tool, parse_tool_calls, get_all_tools
    
    data = request.get_json() or {}
    message = data.get('message', '')
    history = data.get('history', [])
    enable_tools = data.get('enableTools', True)
    
    if not message:
        return jsonify({'error': 'Message is required'}), 400
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        tool_results = []
        
        # Build system prompt with tool instructions
        tool_names = ', '.join([t['name'] for t in get_all_tools()])
        system_prompt = f"""You are Pearto AI. You MUST use tools for ALL data requests. Output tool calls in this format:

<tool_call>{{"name": "tool_name", "arguments": {{...}}}}</tool_call>

AVAILABLE TOOLS: {tool_names}

NATURAL LANGUAGE MAPPING:
- "stock price of [company]" → get_stock_quote (Tesla→TSLA, Apple→AAPL, Google→GOOGL)
- "calculate SIP/investment" → calculate_sip
- "calculate EMI/loan" → calculate_emi
- "forex/exchange rate" → get_forex_rates
- "weather in [city]" → get_weather
- "top gainers/losers" → get_market_movers
- "crypto price" → get_crypto_price
- "news about" → search_news

RULES:
1. ALWAYS call a tool for data requests
2. After tool results, provide a friendly summary
3. Be concise and helpful"""
        
        # Initial AI call
        messages = [
            {"role": "system", "content": system_prompt},
            *history[-6:],
            {"role": "user", "content": message}
        ]
        
        context = {'page_type': 'assistant', 'history': messages[:-1]}
        ai_result = loop.run_until_complete(ai_service.chat(message, context, {'max_tokens': 1000}))
        ai_response = ai_result.get('response', '')
        
        # Parse and execute tools if enabled
        if enable_tools:
            iterations = 0
            max_iterations = 3
            
            while iterations < max_iterations:
                tool_calls = parse_tool_calls(ai_response)
                
                if not tool_calls:
                    break
                    
                iterations += 1
                
                # Execute all tool calls
                for tool_call in tool_calls:
                    try:
                        result = loop.run_until_complete(
                            execute_tool(tool_call['name'], tool_call.get('arguments', {}), {})
                        )
                        tool_results.append({
                            'tool': tool_call['name'],
                            'args': tool_call.get('arguments', {}),
                            'result': result
                        })
                    except Exception as e:
                        tool_results.append({
                            'tool': tool_call['name'],
                            'args': tool_call.get('arguments', {}),
                            'result': {'error': str(e)}
                        })
                
                # Call AI again with tool results
                tool_results_text = '\n\n'.join([
                    f"Tool: {tr['tool']}\nResult: {tr['result']}"
                    for tr in tool_results
                ])
                
                messages.append({"role": "assistant", "content": ai_response})
                messages.append({
                    "role": "user", 
                    "content": f"<tool_results>\n{tool_results_text}\n</tool_results>\n\nNow provide a helpful summary. Do not call any more tools."
                })
                
                ai_result = loop.run_until_complete(ai_service.chat(
                    messages[-1]['content'], 
                    {'page_type': 'assistant', 'history': messages[:-1]},
                    {'max_tokens': 800}
                ))
                ai_response = ai_result.get('response', '')
        
        # Clean final response of tool blocks
        final_response = ai_response
        for pattern in [
            r'<tool_call>[\s\S]*?</tool_call>',
            r'<tool_results>[\s\S]*?</tool_results>',
            r'```(?:json|tool)?\s*\{[\s\S]*?\}\s*```'
        ]:
            final_response = re.sub(pattern, '', final_response, flags=re.IGNORECASE).strip()
        
        return jsonify({
            'success': True,
            'response': final_response,
            'toolsUsed': tool_results,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        loop.close()


@ai_bp.route('/analyze', methods=['POST'])
def analyze():
    """Analyze page data and return insights"""
    from services.ai_service import ai_service
    
    data = request.get_json() or {}
    page_type = data.get('pageType', 'general')
    page_data = data.get('pageData', {})
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        # Build analysis prompt
        prompt = f"""Analyze this {page_type} data and provide 2-3 specific insights.
Format each insight as a single concise sentence (max 50 chars each).
Focus on trends, opportunities, or key observations.

Data: {str(page_data)[:500]}

Provide insights as bullet points starting with •"""

        context = {'page_type': page_type, 'page_data': page_data}
        result = loop.run_until_complete(ai_service.chat(prompt, context, {'max_tokens': 300}))
        
        response_text = result.get('response', '')
        
        # Parse insights from response
        insights = []
        for line in response_text.split('\n'):
            line = line.strip()
            if line.startswith('•') or line.startswith('-') or line.startswith('*'):
                insight = line.lstrip('•-* ').strip()
                if insight and len(insight) > 5:
                    insights.append(insight[:80])  # Limit length
        
        return jsonify({
            'success': True,
            'analysis': response_text,
            'insights': insights[:3],  # Max 3 insights
            'provider': result.get('provider', 'SathiAI'),
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'insights': []
        }), 500
    finally:
        loop.close()


@ai_bp.route('/tools', methods=['GET'])
def get_tools():
    """Get list of available tools"""
    from services.ai_tools import get_all_tools
    
    tools = get_all_tools()
    return jsonify({
        'success': True,
        'tools': tools,
        'count': len(tools)
    })


@ai_bp.route('/execute-tool', methods=['POST'])
def execute_tool_endpoint():
    """Execute a specific tool directly"""
    from services.ai_tools import execute_tool
    
    data = request.get_json() or {}
    tool_name = data.get('tool', '')
    args = data.get('args', {})
    
    if not tool_name:
        return jsonify({'error': 'Tool name is required'}), 400
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        result = loop.run_until_complete(execute_tool(tool_name, args, {}))
        return jsonify({
            'success': True,
            'tool': tool_name,
            'result': result,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        loop.close()


@ai_bp.route('/status', methods=['GET'])
def get_status():
    """Check AI service status"""
    from services.ai_service import ai_service
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        status = loop.run_until_complete(ai_service.get_status())
        return jsonify(status)
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        })
    finally:
        loop.close()
