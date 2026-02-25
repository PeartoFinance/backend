"""
AI API Routes
Chat, analyze, tool execution, comparison, screener & market intelligence endpoints
"""
import re
import json
import asyncio
from flask import Blueprint, jsonify, request
from datetime import datetime

ai_bp = Blueprint('ai', __name__)


def _run_async(coro):
    """Helper to run async functions in sync Flask routes"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@ai_bp.route('/chat', methods=['POST'])
def chat():
    """Basic chat endpoint"""
    from services.ai_service import ai_service
    
    data = request.get_json() or {}
    message = data.get('message', '')
    context = data.get('context', {})
    
    if not message:
        return jsonify({'error': 'Message is required'}), 400
    
    try:
        result = _run_async(ai_service.chat(message, context))
        return jsonify({
            'success': result.get('success', False),
            'response': result.get('response', ''),
            'provider': result.get('provider', 'unknown'),
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@ai_bp.route('/chat-with-tools', methods=['POST'])
def chat_with_tools():
    """Chat endpoint with tool execution and multi-step reasoning"""
    from services.ai_service import ai_service
    from services.ai_tools import execute_tool, parse_tool_calls, get_all_tools
    
    data = request.get_json() or {}
    message = data.get('message', '')
    history = data.get('history', [])
    enable_tools = data.get('enableTools', True)
    mode = data.get('mode', 'default')  # default, deep-analysis, quick
    
    if not message:
        return jsonify({'error': 'Message is required'}), 400
    
    try:
        tool_results = []
        
        # Build system prompt with tool instructions
        tools = get_all_tools()
        tool_defs = json.dumps([{'name': t['name'], 'description': t['description'], 'parameters': list(t.get('parameters', {}).keys())} for t in tools], indent=1)
        
        mode_instructions = {
            'deep-analysis': """
MODE: Deep Analysis — Provide thorough, detailed analysis with multiple data points.
- Use MULTIPLE tools to cross-reference data
- Provide comprehensive insights with numbers, comparisons, and context
- Include risk factors, outlook, and actionable recommendations
- Format with headers, bullet points, and clear structure""",
            'quick': """
MODE: Quick Answer — Be extremely concise.
- One tool call max, brief 2-3 sentence response
- Skip detailed analysis, just give the key number/fact""",
            'default': """
MODE: Standard — Balance detail with brevity.
- Use tools as needed, provide a helpful summary
- Include key metrics and a brief insight"""
        }
        
        system_prompt = f"""You are **Pearto AI**, an advanced financial intelligence assistant. You help users with stocks, crypto, forex, calculators, portfolio analysis, market screening, and financial planning.

{mode_instructions.get(mode, mode_instructions['default'])}

OUTPUT TOOL CALLS IN THIS FORMAT:
<tool_call>{{"name": "tool_name", "arguments": {{...}}}}</tool_call>

AVAILABLE TOOLS:
{tool_defs}

SMART MAPPING (resolve natural language to the right tool + args):
- Company names → ticker symbols (Tesla→TSLA, Apple→AAPL, Google→GOOGL, Microsoft→MSFT, Amazon→AMZN, Meta→META, Nvidia→NVDA)
- "compare X and Y" / "X vs Y" → compare_stocks with both symbols
- "screen/find stocks with..." → screen_stocks with criteria
- "stock price / quote" → get_stock_quote
- "crypto price" → get_crypto_price  
- "top gainers/losers" → get_market_movers
- "SIP/investment calculator" → calculate_sip
- "EMI/loan calculator" → calculate_emi
- "compound interest" → calculate_compound_interest
- "forex/exchange rate" → get_forex_rates
- "weather" → get_weather
- "news about" → search_news
- "sector/industry performance" → get_sector_performance
- "technical analysis / RSI / moving average" → get_technical_indicators

RULES:
1. ALWAYS call a tool for any data/number request — never make up prices or stats
2. You may chain multiple tools in a single response for comparison queries
3. After receiving tool results, provide a clear, well-formatted summary with insights
4. Use **bold** for key numbers, markdown tables for comparisons
5. Add brief actionable insight or context where appropriate
6. Never output raw JSON to the user"""
        
        context_data = data.get('context', {})
        
        if context_data and isinstance(context_data, dict):
            page_type = context_data.get('pageType', 'general')
            page_data = context_data.get('pageData', {})
            
            system_prompt += f"\n\nCURRENT PAGE CONTEXT ({page_type}):\n"
            for key, value in page_data.items():
                system_prompt += f"- {key}: {value}\n"
                
        # Initial AI call
        messages = [
            {"role": "system", "content": system_prompt},
            *history[-10:],
            {"role": "user", "content": message}
        ]
        
        max_tokens = {'deep-analysis': 1500, 'quick': 400}.get(mode, 1000)
        
        ai_context = {'page_type': 'assistant', 'history': messages[:-1]}
        ai_result = _run_async(ai_service.chat(message, ai_context, {'max_tokens': max_tokens}))
        ai_response = ai_result.get('response', '')
        
        # Parse and execute tools if enabled
        if enable_tools:
            iterations = 0
            max_iterations = 4 if mode == 'deep-analysis' else 3
            
            while iterations < max_iterations:
                tool_calls = parse_tool_calls(ai_response)
                
                if not tool_calls:
                    break
                    
                iterations += 1
                
                # Execute all tool calls (parallel-safe since they're independent)
                for tool_call in tool_calls:
                    try:
                        result = _run_async(
                            execute_tool(tool_call['name'], tool_call.get('arguments', {}), context_data)
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
                    f"Tool: {tr['tool']}\nArguments: {json.dumps(tr['args'])}\nResult: {json.dumps(tr['result'], default=str)}"
                    for tr in tool_results
                ])
                
                messages.append({"role": "assistant", "content": ai_response})
                messages.append({
                    "role": "user", 
                    "content": f"<tool_results>\n{tool_results_text}\n</tool_results>\n\nNow provide a well-formatted, insightful summary based on the data above. Use markdown formatting (bold, tables, bullet points). Do NOT call any more tools. Do NOT output raw JSON."
                })
                
                ai_result = _run_async(ai_service.chat(
                    messages[-1]['content'], 
                    {'page_type': 'assistant', 'history': messages[:-1]},
                    {'max_tokens': max_tokens}
                ))
                ai_response = ai_result.get('response', '')
        
        # Clean final response of any leaked tool blocks
        final_response = ai_response
        for pattern in [
            r'<tool_call>[\s\S]*?</tool_call>',
            r'<tool_results>[\s\S]*?</tool_results>',
            r'```(?:json|tool)?\s*\{[\s\S]*?\}\s*```',
            r'\{\s*"name"\s*:\s*"[^"]+"\s*,\s*"arguments"\s*:\s*\{[^}]*\}\s*\}'
        ]:
            final_response = re.sub(pattern, '', final_response, flags=re.IGNORECASE).strip()
        
        # Detect suggested follow-up questions from the response
        follow_ups = []
        follow_up_match = re.findall(r'(?:^|\n)\s*[-•]\s*(.+\?)\s*$', final_response, re.MULTILINE)
        if follow_up_match and len(follow_up_match) >= 2:
            follow_ups = [q.strip() for q in follow_up_match[:3]]
        
        return jsonify({
            'success': True,
            'response': final_response,
            'toolsUsed': tool_results,
            'followUpQuestions': follow_ups,
            'mode': mode,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@ai_bp.route('/compare', methods=['POST'])
def compare_assets():
    """Compare two or more stocks/cryptos side by side"""
    from services.ai_tools import execute_tool
    
    data = request.get_json() or {}
    symbols = data.get('symbols', [])
    
    if len(symbols) < 2:
        return jsonify({'error': 'At least 2 symbols required'}), 400
    
    try:
        results = {}
        for symbol in symbols[:5]:  # Max 5
            try:
                result = _run_async(execute_tool('get_stock_quote', {'symbol': symbol}, {}))
                if result.get('error'):
                    result = _run_async(execute_tool('get_crypto_price', {'symbol': symbol}, {}))
                results[symbol] = result
            except Exception as e:
                results[symbol] = {'error': str(e)}
        
        return jsonify({
            'success': True,
            'comparison': results,
            'symbols': symbols,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@ai_bp.route('/screen', methods=['POST'])
def screen_stocks():
    """AI-powered stock screener"""
    from services.ai_tools import execute_tool
    
    data = request.get_json() or {}
    criteria = data.get('criteria', {})
    
    try:
        result = _run_async(execute_tool('screen_stocks', criteria, {}))
        return jsonify({
            'success': True,
            'results': result,
            'criteria': criteria,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@ai_bp.route('/quick-insights', methods=['POST'])
def quick_insights():
    """Generate multiple quick insights for a symbol or topic"""
    from services.ai_service import ai_service
    from services.ai_tools import execute_tool
    
    data = request.get_json() or {}
    symbol = data.get('symbol', '')
    insight_type = data.get('type', 'overview')  # overview, technical, fundamental
    
    if not symbol:
        return jsonify({'error': 'Symbol is required'}), 400
    
    try:
        # Fetch data first
        stock_data = _run_async(execute_tool('get_stock_quote', {'symbol': symbol}, {}))
        
        if stock_data.get('error'):
            return jsonify({'error': f'Could not fetch data for {symbol}'}), 404
        
        prompt_map = {
            'overview': f"""Given this stock data for {symbol}: {json.dumps(stock_data, default=str)}
Provide exactly 4 quick insights as JSON array. Each insight should have: "title" (3-5 words), "value" (the key metric), "sentiment" (bullish/bearish/neutral), "detail" (one sentence).
Return ONLY valid JSON array, no other text.""",
            'technical': f"""Given this stock data for {symbol}: {json.dumps(stock_data, default=str)}
Provide 4 technical analysis insights as JSON array. Each: "title", "value", "sentiment" (bullish/bearish/neutral), "detail".
Focus on price action, volume, momentum, support/resistance.
Return ONLY valid JSON array.""",
            'fundamental': f"""Given this stock data for {symbol}: {json.dumps(stock_data, default=str)}
Provide 4 fundamental analysis insights as JSON array. Each: "title", "value", "sentiment" (bullish/bearish/neutral), "detail".
Focus on P/E, market cap, earnings, dividends, valuation.
Return ONLY valid JSON array."""
        }
        
        result = _run_async(ai_service.chat(
            prompt_map.get(insight_type, prompt_map['overview']),
            {'page_type': 'insights'},
            {'max_tokens': 500}
        ))
        
        # Parse JSON from response
        response_text = result.get('response', '[]')
        try:
            # Try to extract JSON array
            json_match = re.search(r'\[[\s\S]*\]', response_text)
            insights = json.loads(json_match.group()) if json_match else []
        except (json.JSONDecodeError, AttributeError):
            insights = [{"title": "Data Available", "value": f"${stock_data.get('price', 'N/A')}", "sentiment": "neutral", "detail": response_text[:100]}]
        
        return jsonify({
            'success': True,
            'symbol': symbol,
            'type': insight_type,
            'insights': insights[:4],
            'stockData': stock_data,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@ai_bp.route('/analyze', methods=['POST'])
def analyze():
    """Analyze page data and return insights"""
    from services.ai_service import ai_service
    
    data = request.get_json() or {}
    page_type = data.get('pageType', 'general')
    page_data = data.get('pageData', {})
    
    try:
        prompt = f"""Analyze this {page_type} data and provide 2-3 specific insights.
Format each insight as a single concise sentence (max 50 chars each).
Focus on trends, opportunities, or key observations.

Data: {str(page_data)[:500]}

Provide insights as bullet points starting with •"""

        context = {'page_type': page_type, 'page_data': page_data}
        result = _run_async(ai_service.chat(prompt, context, {'max_tokens': 300}))
        
        response_text = result.get('response', '')
        
        insights = []
        for line in response_text.split('\n'):
            line = line.strip()
            if line.startswith('•') or line.startswith('-') or line.startswith('*'):
                insight = line.lstrip('•-* ').strip()
                if insight and len(insight) > 5:
                    insights.append(insight[:80])
        
        return jsonify({
            'success': True,
            'analysis': response_text,
            'insights': insights[:3],
            'provider': result.get('provider', 'SathiAI'),
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'insights': []
        }), 500


@ai_bp.route('/tools', methods=['GET'])
def get_tools():
    """Get list of available tools with descriptions"""
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
    
    try:
        result = _run_async(execute_tool(tool_name, args, {}))
        return jsonify({
            'success': True,
            'tool': tool_name,
            'result': result,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@ai_bp.route('/status', methods=['GET'])
def get_status():
    """Check AI service status"""
    from services.ai_service import ai_service
    
    try:
        status = _run_async(ai_service.get_status())
        return jsonify(status)
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        })
