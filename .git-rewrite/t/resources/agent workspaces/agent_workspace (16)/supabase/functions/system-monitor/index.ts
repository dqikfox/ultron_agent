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
        const action = url.searchParams.get('action') || 'stats';

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

        if (action === 'stats') {
            console.log('Collecting system statistics...');

            // Simulate system stats (in a real implementation, you'd collect actual system data)
            // For this demo, we'll generate realistic-looking stats
            const now = Date.now();
            const cpuUsage = 15 + Math.sin(now / 30000) * 10 + Math.random() * 5;
            const memoryUsage = 45 + Math.sin(now / 45000) * 15 + Math.random() * 8;
            const diskUsage = 67 + Math.random() * 3;
            const gpuUsage = 8 + Math.sin(now / 20000) * 12 + Math.random() * 6;
            const temperature = 35 + Math.sin(now / 25000) * 8 + Math.random() * 4;

            // Check Ollama status
            let ollamaStatus = 'unknown';
            let activeModel = null;
            
            try {
                const ollamaResponse = await fetch('http://localhost:11434/api/tags', {
                    method: 'GET',
                    headers: { 'Content-Type': 'application/json' }
                });
                
                if (ollamaResponse.ok) {
                    ollamaStatus = 'running';
                    // Try to get the last used model
                    const modelsData = await ollamaResponse.json();
                    if (modelsData.models && modelsData.models.length > 0) {
                        activeModel = modelsData.models[0].name; // Use first available model as active
                    }
                } else {
                    ollamaStatus = 'error';
                }
            } catch (error) {
                ollamaStatus = 'stopped';
                console.log('Ollama not available:', error.message);
            }

            const systemStats = {
                cpu_usage: parseFloat(cpuUsage.toFixed(2)),
                memory_usage: parseFloat(memoryUsage.toFixed(2)),
                memory_total_gb: 16.0,
                disk_usage: parseFloat(diskUsage.toFixed(2)),
                disk_total_gb: 512.0,
                ollama_status: ollamaStatus,
                active_model: activeModel,
                gpu_usage: parseFloat(gpuUsage.toFixed(2)),
                temperature: parseFloat(temperature.toFixed(2)),
                uptime_seconds: Math.floor(Date.now() / 1000) % 86400, // Simulated daily uptime
                recorded_at: new Date().toISOString()
            };

            // Save stats to database
            const statsResponse = await fetch(`${supabaseUrl}/rest/v1/system_stats`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${serviceRoleKey}`,
                    'apikey': serviceRoleKey,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(systemStats)
            });

            if (!statsResponse.ok) {
                console.error('Failed to save system stats');
            }

            // Clean up old stats (keep only last 1000 records)
            try {
                const cleanupResponse = await fetch(
                    `${supabaseUrl}/rest/v1/system_stats?id=lt.(SELECT id FROM system_stats ORDER BY recorded_at DESC LIMIT 1 OFFSET 1000)`,
                    {
                        method: 'DELETE',
                        headers: {
                            'Authorization': `Bearer ${serviceRoleKey}`,
                            'apikey': serviceRoleKey
                        }
                    }
                );
                console.log('Cleanup completed:', cleanupResponse.ok);
            } catch (cleanupError) {
                console.log('Cleanup failed:', cleanupError.message);
            }

            // Log the monitoring action
            const logData = {
                user_id: userId,
                action_type: 'system_monitor',
                action_description: `System stats collected - CPU: ${systemStats.cpu_usage}%, Memory: ${systemStats.memory_usage}%`,
                status: 'success',
                metadata: {
                    cpu_usage: systemStats.cpu_usage,
                    memory_usage: systemStats.memory_usage,
                    ollama_status: ollamaStatus,
                    active_model: activeModel
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
                    stats: systemStats,
                    timestamp: new Date().toISOString(),
                    status: 'healthy'
                }
            }), {
                headers: { ...corsHeaders, 'Content-Type': 'application/json' }
            });
        }

        if (action === 'history') {
            // Get recent system stats history
            const limit = url.searchParams.get('limit') || '100';
            
            const historyResponse = await fetch(
                `${supabaseUrl}/rest/v1/system_stats?order=recorded_at.desc&limit=${limit}`,
                {
                    headers: {
                        'Authorization': `Bearer ${serviceRoleKey}`,
                        'apikey': serviceRoleKey
                    }
                }
            );

            if (!historyResponse.ok) {
                throw new Error('Failed to fetch system stats history');
            }

            const historyData = await historyResponse.json();

            return new Response(JSON.stringify({
                data: {
                    history: historyData.reverse(), // Reverse to get chronological order
                    count: historyData.length
                }
            }), {
                headers: { ...corsHeaders, 'Content-Type': 'application/json' }
            });
        }

        if (action === 'logs') {
            // Get recent system logs
            const limit = url.searchParams.get('limit') || '50';
            const type = url.searchParams.get('type'); // Filter by action type
            
            let query = `${supabaseUrl}/rest/v1/system_logs?order=created_at.desc&limit=${limit}`;
            if (type) {
                query += `&action_type=eq.${type}`;
            }

            const logsResponse = await fetch(query, {
                headers: {
                    'Authorization': `Bearer ${serviceRoleKey}`,
                    'apikey': serviceRoleKey
                }
            });

            if (!logsResponse.ok) {
                throw new Error('Failed to fetch system logs');
            }

            const logsData = await logsResponse.json();

            return new Response(JSON.stringify({
                data: {
                    logs: logsData,
                    count: logsData.length
                }
            }), {
                headers: { ...corsHeaders, 'Content-Type': 'application/json' }
            });
        }

        throw new Error('Invalid action');

    } catch (error) {
        console.error('System monitor error:', error);

        const errorResponse = {
            error: {
                code: 'SYSTEM_MONITOR_FAILED',
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