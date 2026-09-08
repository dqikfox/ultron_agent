Deno.serve(async (req) => {
    const corsHeaders = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
        'Access-Control-Allow-Methods': 'POST, GET, OPTIONS, PUT, DELETE, PATCH',
        'Access-Control-Max-Age': '86400',
        'Access-Control-Allow-Credentials': 'false'
    };

    if (req.method === 'OPTIONS') {
        return new Response(null, { status: 200, headers: corsHeaders });
    }

    try {
        const { message, model = 'llama2', sessionId, stream = false } = await req.json();

        if (!message) {
            throw new Error('Message is required');
        }

        console.log('Chat request:', { message: message.substring(0, 100), model, sessionId });

        // Get environment variables
        const serviceRoleKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');
        const supabaseUrl = Deno.env.get('SUPABASE_URL');

        if (!serviceRoleKey || !supabaseUrl) {
            throw new Error('Supabase configuration missing');
        }

        // Get user from auth header
        let userId = null;
        const authHeader = req.headers.get('authorization');
        if (authHeader) {
            try {
                const token = authHeader.replace('Bearer ', '');
                const userResponse = await fetch(`${supabaseUrl}/auth/v1/user`, {
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'apikey': serviceRoleKey
                    }
                });
                if (userResponse.ok) {
                    const userData = await userResponse.json();
                    userId = userData.id;
                }
            } catch (error) {
                console.log('Could not get user from token:', error.message);
            }
        }

        const startTime = Date.now();

        // Save user message to database
        const userMessageData = {
            user_id: userId,
            session_id: sessionId || crypto.randomUUID(),
            role: 'user',
            content: message,
            model_name: model,
            created_at: new Date().toISOString()
        };

        const userMessageResponse = await fetch(`${supabaseUrl}/rest/v1/chat_messages`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${serviceRoleKey}`,
                'apikey': serviceRoleKey,
                'Content-Type': 'application/json',
                'Prefer': 'return=representation'
            },
            body: JSON.stringify(userMessageData)
        });

        if (!userMessageResponse.ok) {
            console.error('Failed to save user message');
        }

        // Make request to Ollama API
        console.log('Calling Ollama API with model:', model);
        
        const ollamaResponse = await fetch('http://localhost:11434/api/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                model: model,
                prompt: message,
                stream: false
            })
        });

        if (!ollamaResponse.ok) {
            const errorText = await ollamaResponse.text();
            console.error('Ollama API error:', errorText);
            throw new Error(`Ollama API error: ${errorText}`);
        }

        const ollamaData = await ollamaResponse.json();
        const responseTime = Date.now() - startTime;

        console.log('Ollama response received:', {
            responseLength: ollamaData.response?.length || 0,
            responseTime,
            model: ollamaData.model
        });

        // Save assistant response to database
        const assistantMessageData = {
            user_id: userId,
            session_id: sessionId || crypto.randomUUID(),
            role: 'assistant',
            content: ollamaData.response || 'No response from model',
            model_name: model,
            tokens_used: ollamaData.eval_count || 0,
            response_time_ms: responseTime,
            metadata: {
                total_duration: ollamaData.total_duration,
                load_duration: ollamaData.load_duration,
                prompt_eval_count: ollamaData.prompt_eval_count,
                eval_count: ollamaData.eval_count,
                eval_duration: ollamaData.eval_duration
            },
            created_at: new Date().toISOString()
        };

        const assistantMessageResponse = await fetch(`${supabaseUrl}/rest/v1/chat_messages`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${serviceRoleKey}`,
                'apikey': serviceRoleKey,
                'Content-Type': 'application/json',
                'Prefer': 'return=representation'
            },
            body: JSON.stringify(assistantMessageData)
        });

        if (!assistantMessageResponse.ok) {
            console.error('Failed to save assistant message');
        }

        // Log the action
        const logData = {
            user_id: userId,
            action_type: 'ollama_chat',
            action_description: `Chat with ${model} model - ${responseTime}ms response time`,
            status: 'success',
            metadata: {
                model: model,
                session_id: sessionId,
                tokens_used: ollamaData.eval_count || 0,
                response_time_ms: responseTime
            },
            created_at: new Date().toISOString()
        };

        await fetch(`${supabaseUrl}/rest/v1/system_logs`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${serviceRoleKey}`,
                'apikey': serviceRoleKey,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(logData)
        });

        // Return successful response
        return new Response(JSON.stringify({
            data: {
                response: ollamaData.response,
                model: model,
                sessionId: sessionId || crypto.randomUUID(),
                responseTime: responseTime,
                tokensUsed: ollamaData.eval_count || 0,
                metadata: {
                    total_duration: ollamaData.total_duration,
                    load_duration: ollamaData.load_duration,
                    prompt_eval_count: ollamaData.prompt_eval_count,
                    eval_count: ollamaData.eval_count,
                    eval_duration: ollamaData.eval_duration
                }
            }
        }), {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });

    } catch (error) {
        console.error('Ollama chat error:', error);

        const errorResponse = {
            error: {
                code: 'OLLAMA_CHAT_FAILED',
                message: error.message,
                timestamp: new Date().toISOString()
            }
        };

        return new Response(JSON.stringify(errorResponse), {
            status: 500,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
    }
});