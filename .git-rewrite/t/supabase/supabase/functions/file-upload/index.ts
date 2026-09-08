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
        const { fileData, fileName, fileType, aiAnalysis = false } = await req.json();

        if (!fileData || !fileName) {
            throw new Error('File data and filename are required');
        }

        // Get environment variables
        const serviceRoleKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');
        const supabaseUrl = Deno.env.get('SUPABASE_URL');
        const openaiKey = Deno.env.get('OPENAI_API_KEY');

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

        // Extract base64 data from data URL
        const base64Data = fileData.split(',')[1];
        const mimeType = fileData.split(';')[0].split(':')[1];

        // Convert base64 to binary
        const binaryData = Uint8Array.from(atob(base64Data), c => c.charCodeAt(0));

        // Generate unique filename
        const timestamp = Date.now();
        const uniqueFileName = `${timestamp}-${fileName}`;

        // Upload to Supabase Storage
        const uploadResponse = await fetch(`${supabaseUrl}/storage/v1/object/file-uploads/${uniqueFileName}`, {
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
            throw new Error(`Upload failed: ${errorText}`);
        }

        // Get public URL
        const publicUrl = `${supabaseUrl}/storage/v1/object/public/file-uploads/${uniqueFileName}`;

        // Process file based on type
        let ocrText = null;
        let aiAnalysisResult = null;
        let processingStatus = 'completed';

        // OCR for images
        if (fileType.startsWith('image/') && openaiKey) {
            try {
                const ocrResult = await performOCR(fileData, openaiKey);
                ocrText = ocrResult;
            } catch (error) {
                console.error('OCR failed:', error);
            }
        }

        // AI analysis if requested
        if (aiAnalysis && openaiKey) {
            try {
                const analysisResult = await performAIAnalysis(fileData, fileType, ocrText, openaiKey);
                aiAnalysisResult = analysisResult;
            } catch (error) {
                console.error('AI analysis failed:', error);
            }
        }

        // Save file metadata to database
        const insertResponse = await fetch(`${supabaseUrl}/rest/v1/file_uploads`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${serviceRoleKey}`,
                'apikey': serviceRoleKey,
                'Content-Type': 'application/json',
                'Prefer': 'return=representation'
            },
            body: JSON.stringify({
                user_id: userId,
                filename: fileName,
                file_url: publicUrl,
                file_type: fileType,
                file_size: binaryData.length,
                processing_status: processingStatus,
                ocr_text: ocrText,
                ai_analysis: aiAnalysisResult,
                processed_at: new Date().toISOString()
            })
        });

        if (!insertResponse.ok) {
            const errorText = await insertResponse.text();
            throw new Error(`Database insert failed: ${errorText}`);
        }

        const fileRecord = await insertResponse.json();

        return new Response(JSON.stringify({
            data: {
                fileUrl: publicUrl,
                file: fileRecord[0],
                ocrText,
                aiAnalysis: aiAnalysisResult
            }
        }), {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });

    } catch (error) {
        console.error('File upload error:', error);
        return new Response(JSON.stringify({
            error: {
                code: 'FILE_UPLOAD_FAILED',
                message: error.message
            }
        }), {
            status: 500,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
    }
});

// OCR using OpenAI Vision
async function performOCR(imageData, apiKey) {
    const response = await fetch('https://api.openai.com/v1/chat/completions', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${apiKey}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            model: 'gpt-4-vision-preview',
            messages: [{
                role: 'user',
                content: [{
                    type: 'text',
                    text: 'Extract all text from this image. Return only the text content, no additional commentary.'
                }, {
                    type: 'image_url',
                    image_url: {
                        url: imageData
                    }
                }]
            }],
            max_tokens: 1000
        })
    });

    if (!response.ok) {
        throw new Error('OCR failed');
    }

    const data = await response.json();
    return data.choices[0].message.content;
}

// AI analysis of files
async function performAIAnalysis(fileData, fileType, ocrText, apiKey) {
    let prompt = '';
    
    if (fileType.startsWith('image/')) {
        prompt = 'Analyze this image and provide insights about its content, objects, colors, composition, and any notable features.';
        if (ocrText) {
            prompt += ` The image also contains this text: "${ocrText}"`;
        }
    } else if (fileType === 'application/pdf' || fileType.startsWith('text/')) {
        prompt = 'Analyze this document and provide a summary of its key points, main topics, and important information.';
    } else {
        prompt = 'Analyze this file and provide insights about its content and structure.';
    }

    const messages = [{
        role: 'user',
        content: fileType.startsWith('image/') ? [{
            type: 'text',
            text: prompt
        }, {
            type: 'image_url',
            image_url: {
                url: fileData
            }
        }] : prompt
    }];

    const response = await fetch('https://api.openai.com/v1/chat/completions', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${apiKey}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            model: fileType.startsWith('image/') ? 'gpt-4-vision-preview' : 'gpt-3.5-turbo',
            messages,
            max_tokens: 1000
        })
    });

    if (!response.ok) {
        throw new Error('AI analysis failed');
    }

    const data = await response.json();
    return data.choices[0].message.content;
}