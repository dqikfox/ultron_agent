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
        const url = new URL(req.url);
        const action = url.searchParams.get('action') || 'list';

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

        if (action === 'list') {
            // Get available models from Ollama
            console.log('Fetching available models from Ollama...');
            
            try {
                const ollamaResponse = await fetch('http://localhost:11434/api/tags', {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });

                if (!ollamaResponse.ok) {
                    throw new Error('Ollama API not available');
                }

                const ollamaData = await ollamaResponse.json();
                console.log('Ollama models found:', ollamaData.models?.length || 0);

                // Update database with current models
                for (const model of ollamaData.models || []) {
                    const modelData = {
                        name: model.name,
                        display_name: model.name.charAt(0).toUpperCase() + model.name.slice(1),
                        description: `${model.name} model`,
                        size_gb: model.size ? parseFloat((model.size / (1024 * 1024 * 1024)).toFixed(2)) : 0,
                        is_available: true,
                        is_downloading: false,
                        download_progress: 100,
                        updated_at: new Date().toISOString()
                    };

                    // Upsert model data
                    await fetch(`${supabaseUrl}/rest/v1/ollama_models`, {
                        method: 'POST',
                        headers: {
                            'Authorization': `Bearer ${serviceRoleKey}`,
                            'apikey': serviceRoleKey,
                            'Content-Type': 'application/json',
                            'Prefer': 'resolution=merge-duplicates'
                        },
                        body: JSON.stringify(modelData)
                    });
                }

                // Get models from database
                const dbResponse = await fetch(`${supabaseUrl}/rest/v1/ollama_models?order=name.asc`, {
                    headers: {
                        'Authorization': `Bearer ${serviceRoleKey}`,
                        'apikey': serviceRoleKey
                    }
                });

                const dbModels = await dbResponse.json();

                // Log the action
                const logData = {
                    user_id: userId,
                    action_type: 'ollama_models_list',
                    action_description: `Listed ${dbModels.length} available models`,
                    status: 'success',
                    metadata: {
                        models_count: dbModels.length,
                        ollama_available: true
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

                return new Response(JSON.stringify({
                    data: {
                        models: dbModels,
                        ollama_status: 'running',
                        total_models: dbModels.length
                    }
                }), {
                    headers: { ...corsHeaders, 'Content-Type': 'application/json' }
                });

            } catch (ollamaError) {
                console.error('Ollama connection failed:', ollamaError.message);
                
                // Return cached models from database with error status
                const dbResponse = await fetch(`${supabaseUrl}/rest/v1/ollama_models?order=name.asc`, {
                    headers: {
                        'Authorization': `Bearer ${serviceRoleKey}`,
                        'apikey': serviceRoleKey
                    }
                });

                const dbModels = await dbResponse.json();

                return new Response(JSON.stringify({
                    data: {
                        models: dbModels,
                        ollama_status: 'error',
                        error_message: 'Ollama API not available',
                        total_models: dbModels.length
                    }
                }), {
                    headers: { ...corsHeaders, 'Content-Type': 'application/json' }
                });
            }
        }

        if (action === 'pull') {
            const { modelName } = await req.json();
            
            if (!modelName) {
                throw new Error('Model name is required');
            }

            console.log('Pulling model:', modelName);

            // Start model pull in Ollama
            const pullResponse = await fetch('http://localhost:11434/api/pull', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    name: modelName
                })
            });

            if (!pullResponse.ok) {
                throw new Error('Failed to start model download');
            }

            // Update model status in database
            const modelData = {
                name: modelName,
                display_name: modelName.charAt(0).toUpperCase() + modelName.slice(1),
                description: `${modelName} model`,
                is_available: false,
                is_downloading: true,
                download_progress: 0,
                updated_at: new Date().toISOString()
            };

            await fetch(`${supabaseUrl}/rest/v1/ollama_models`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${serviceRoleKey}`,
                    'apikey': serviceRoleKey,
                    'Content-Type': 'application/json',
                    'Prefer': 'resolution=merge-duplicates'
                },
                body: JSON.stringify(modelData)
            });

            return new Response(JSON.stringify({
                data: {
                    message: `Started downloading ${modelName}`,
                    model_name: modelName,
                    status: 'downloading'
                }
            }), {
                headers: { ...corsHeaders, 'Content-Type': 'application/json' }
            });
        }

        if (action === 'delete') {
            const { modelName } = await req.json();
            
            if (!modelName) {
                throw new Error('Model name is required');
            }

            console.log('Deleting model:', modelName);

            // Delete model from Ollama
            const deleteResponse = await fetch('http://localhost:11434/api/delete', {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    name: modelName
                })
            });

            if (!deleteResponse.ok) {
                throw new Error('Failed to delete model');
            }

            // Remove from database
            await fetch(`${supabaseUrl}/rest/v1/ollama_models?name=eq.${modelName}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${serviceRoleKey}`,
                    'apikey': serviceRoleKey
                }
            });

            return new Response(JSON.stringify({
                data: {
                    message: `Deleted ${modelName}`,
                    model_name: modelName,
                    status: 'deleted'
                }
            }), {
                headers: { ...corsHeaders, 'Content-Type': 'application/json' }
            });
        }

        throw new Error('Invalid action');

    } catch (error) {
        console.error('Ollama models error:', error);

        const errorResponse = {
            error: {
                code: 'OLLAMA_MODELS_FAILED',
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