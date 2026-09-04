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
        const { fileData, fileName, fileType, sessionId } = await req.json();

        if (!fileData || !fileName) {
            throw new Error('File data and filename are required');
        }

        console.log('File upload request:', { fileName, fileType, sessionId });

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

        // Extract base64 data from data URL
        const base64Data = fileData.split(',')[1];
        const mimeType = fileData.split(';')[0].split(':')[1];

        // Convert base64 to binary
        const binaryData = Uint8Array.from(atob(base64Data), c => c.charCodeAt(0));

        // Generate unique filename with timestamp
        const timestamp = Date.now();
        const uniqueFileName = `${timestamp}-${fileName}`;
        const filePath = `ultron-uploads/${uniqueFileName}`;

        // Upload to Supabase Storage
        const uploadResponse = await fetch(`${supabaseUrl}/storage/v1/object/ultron-files/${filePath}`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${serviceRoleKey}`,
                'Content-Type': mimeType,
                'x-upsert': 'true'
            },
            body: binaryData
        });

        if (!uploadResponse.ok) {
            const errorText = await uploadResponse.text();
            console.error('Upload failed:', errorText);
            
            // If bucket doesn't exist, try to create it
            if (errorText.includes('Bucket not found')) {
                console.log('Creating ultron-files bucket...');
                
                // Create bucket
                const bucketResponse = await fetch(`${supabaseUrl}/storage/v1/bucket`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${serviceRoleKey}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        id: 'ultron-files',
                        name: 'ultron-files',
                        public: true
                    })
                });
                
                if (bucketResponse.ok) {
                    // Retry upload
                    const retryResponse = await fetch(`${supabaseUrl}/storage/v1/object/ultron-files/${filePath}`, {
                        method: 'POST',
                        headers: {
                            'Authorization': `Bearer ${serviceRoleKey}`,
                            'Content-Type': mimeType,
                            'x-upsert': 'true'
                        },
                        body: binaryData
                    });
                    
                    if (!retryResponse.ok) {
                        throw new Error('Upload failed after bucket creation');
                    }
                } else {
                    throw new Error('Failed to create storage bucket');
                }
            } else {
                throw new Error(`Upload failed: ${errorText}`);
            }
        }

        // Get public URL
        const publicUrl = `${supabaseUrl}/storage/v1/object/public/ultron-files/${filePath}`;

        // Save file metadata as a system message in chat
        const fileMessage = {
            user_id: userId,
            session_id: sessionId || crypto.randomUUID(),
            role: 'system',
            content: `File uploaded: ${fileName} (${fileType || mimeType})`,
            model_name: 'system',
            metadata: {
                file_name: fileName,
                file_type: fileType || mimeType,
                file_size: binaryData.length,
                file_url: publicUrl,
                file_path: filePath,
                upload_timestamp: new Date().toISOString()
            },
            created_at: new Date().toISOString()
        };

        const messageResponse = await fetch(`${supabaseUrl}/rest/v1/chat_messages`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${serviceRoleKey}`,
                'apikey': serviceRoleKey,
                'Content-Type': 'application/json',
                'Prefer': 'return=representation'
            },
            body: JSON.stringify(fileMessage)
        });

        if (!messageResponse.ok) {
            console.error('Failed to save file message');
        }

        // Log the upload action
        const logData = {
            user_id: userId,
            action_type: 'file_upload',
            action_description: `Uploaded file: ${fileName} (${(binaryData.length / 1024).toFixed(2)} KB)`,
            status: 'success',
            metadata: {
                file_name: fileName,
                file_type: fileType || mimeType,
                file_size: binaryData.length,
                file_url: publicUrl,
                session_id: sessionId
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
                fileName: fileName,
                fileUrl: publicUrl,
                filePath: filePath,
                fileSize: binaryData.length,
                mimeType: mimeType,
                sessionId: sessionId || crypto.randomUUID(),
                message: 'File uploaded successfully'
            }
        }), {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });

    } catch (error) {
        console.error('File upload error:', error);

        const errorResponse = {
            error: {
                code: 'FILE_UPLOAD_FAILED',
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