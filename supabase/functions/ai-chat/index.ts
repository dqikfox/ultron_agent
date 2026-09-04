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
        const { message, provider, model, conversationId, temperature = 0.7 } = await req.json();

        if (!message || !provider) {
            throw new Error('Message and provider are required');
        }

        // Get environment variables
        const serviceRoleKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');
        const supabaseUrl = Deno.env.get('SUPABASE_URL');
        const openaiKey = Deno.env.get('OPENAI_API_KEY');
        const deepseekKey = Deno.env.get('DEEPSEEK_API_KEY');
        const googleKey = Deno.env.get('GOOGLE_AI_API_KEY');

        if (!serviceRoleKey || !supabaseUrl) {
            throw new Error('Supabase configuration missing');
        }

        // Get user from auth header
        const authHeader = req.headers.get('authorization');
        if (!authHeader) {
            throw new Error('No authorization header');
        }

        const token = authHeader.replace('Bearer ', '');
        const userResponse = await fetch(`${supabaseUrl}/auth/v1/user`, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'apikey': serviceRoleKey
            }
        });

        if (!userResponse.ok) {
            throw new Error('Invalid token');
        }

        const userData = await userResponse.json();
        const userId = userData.id;

        let response;
        const startTime = Date.now();

        // Handle different AI providers
        switch (provider) {
            case 'openai':
                if (!openaiKey) throw new Error('OpenAI API key not configured');
                response = await handleOpenAI(message, model || 'gpt-3.5-turbo', openaiKey, temperature);
                break;
            
            case 'deepseek':
                if (!deepseekKey) throw new Error('DeepSeek API key not configured');
                response = await handleDeepSeek(message, model || 'deepseek-chat', deepseekKey, temperature);
                break;
            
            case 'google':
                if (!googleKey) throw new Error('Google AI API key not configured');
                response = await handleGoogleAI(message, model || 'gemini-pro', googleKey, temperature);
                break;
            
            case 'ollama':
                response = await handleOllama(message, model || 'llama2', temperature);
                break;
            
            default:
                throw new Error(`Unsupported provider: ${provider}`);
        }

        const processingTime = Date.now() - startTime;

        // Save conversation and messages to database
        let convId = conversationId;
        if (!convId) {
            // Create new conversation
            const convResponse = await fetch(`${supabaseUrl}/rest/v1/conversations`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${serviceRoleKey}`,
                    'apikey': serviceRoleKey,
                    'Content-Type': 'application/json',
                    'Prefer': 'return=representation'
                },
                body: JSON.stringify({
                    user_id: userId,
                    title: message.substring(0, 100),
                    ai_provider: provider,
                    model_name: model
                })
            });

            if (convResponse.ok) {
                const convData = await convResponse.json();
                convId = convData[0].id;
            }
        }

        // Save user message
        await fetch(`${supabaseUrl}/rest/v1/messages`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${serviceRoleKey}`,
                'apikey': serviceRoleKey,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                conversation_id: convId,
                user_id: userId,
                role: 'user',
                content: message,
                message_type: 'text'
            })
        });

        // Save assistant response
        await fetch(`${supabaseUrl}/rest/v1/messages`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${serviceRoleKey}`,
                'apikey': serviceRoleKey,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                conversation_id: convId,
                user_id: userId,
                role: 'assistant',
                content: response.content,
                message_type: 'text',
                processing_time_ms: processingTime,
                tokens_used: response.tokens
            })
        });

        return new Response(JSON.stringify({
            data: {
                content: response.content,
                provider,
                model,
                conversationId: convId,
                processingTime,
                tokens: response.tokens
            }
        }), {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });

    } catch (error) {
        console.error('AI chat error:', error);
        return new Response(JSON.stringify({
            error: {
                code: 'AI_CHAT_FAILED',
                message: error.message
            }
        }), {
            status: 500,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
    }
});

// OpenAI handler
async function handleOpenAI(message, model, apiKey, temperature) {
    const response = await fetch('https://api.openai.com/v1/chat/completions', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${apiKey}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            model,
            messages: [{ role: 'user', content: message }],
            temperature,
            max_tokens: 1000
        })
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(`OpenAI API error: ${error.error?.message || 'Unknown error'}`);
    }

    const data = await response.json();
    return {
        content: data.choices[0].message.content,
        tokens: data.usage?.total_tokens || 0
    };
}

// DeepSeek handler
async function handleDeepSeek(message, model, apiKey, temperature) {
    const response = await fetch('https://api.deepseek.com/v1/chat/completions', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${apiKey}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            model,
            messages: [{ role: 'user', content: message }],
            temperature,
            max_tokens: 1000
        })
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(`DeepSeek API error: ${error.error?.message || 'Unknown error'}`);
    }

    const data = await response.json();
    return {
        content: data.choices[0].message.content,
        tokens: data.usage?.total_tokens || 0
    };
}

// Google AI handler
async function handleGoogleAI(message, model, apiKey, temperature) {
    const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${apiKey}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            contents: [{
                parts: [{ text: message }]
            }],
            generationConfig: {
                temperature,
                maxOutputTokens: 1000
            }
        })
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(`Google AI API error: ${error.error?.message || 'Unknown error'}`);
    }

    const data = await response.json();
    return {
        content: data.candidates[0].content.parts[0].text,
        tokens: data.usageMetadata?.totalTokenCount || 0
    };
}

// Ollama handler (local)
async function handleOllama(message, model, temperature) {
    try {
        const response = await fetch('http://localhost:11434/api/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                model,
                prompt: message,
                stream: false,
                options: {
                    temperature
                }
            })
        });

        if (!response.ok) {
            throw new Error(`Ollama API error: ${response.statusText}`);
        }

        const data = await response.json();
        return {
            content: data.response,
            tokens: 0 // Ollama doesn't provide token count
        };
    } catch (error) {
        // Fallback message when Ollama is not available
        return {
            content: "I'm an AI assistant powered by Ultron AI. Ollama service is currently unavailable, but I'm here to help you with any questions or tasks you might have. Please try using one of the other AI providers (OpenAI, DeepSeek, or Google AI) for now.",
            tokens: 0
        };
    }
}