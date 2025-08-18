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
        const { text, voice = 'Rachel', model = 'eleven_multilingual_v2' } = await req.json();

        if (!text) {
            throw new Error('Text is required');
        }

        // Get environment variables
        const elevenlabsKey = Deno.env.get('ELEVENLABS_API_KEY');

        if (!elevenlabsKey) {
            throw new Error('ElevenLabs API key not configured');
        }

        // Get voice ID from voice name
        const voiceId = getVoiceId(voice);

        // Generate speech with ElevenLabs
        const response = await fetch(`https://api.elevenlabs.io/v1/text-to-speech/${voiceId}`, {
            method: 'POST',
            headers: {
                'Accept': 'audio/mpeg',
                'Content-Type': 'application/json',
                'xi-api-key': elevenlabsKey
            },
            body: JSON.stringify({
                text,
                model_id: model,
                voice_settings: {
                    stability: 0.5,
                    similarity_boost: 0.75,
                    style: 0.0,
                    use_speaker_boost: true
                }
            })
        });

        if (!response.ok) {
            const errorData = await response.text();
            throw new Error(`ElevenLabs API error: ${errorData}`);
        }

        // Get audio data
        const audioBuffer = await response.arrayBuffer();
        const audioBase64 = btoa(String.fromCharCode(...new Uint8Array(audioBuffer)));

        return new Response(JSON.stringify({
            data: {
                audioData: `data:audio/mpeg;base64,${audioBase64}`,
                voice,
                model,
                textLength: text.length
            }
        }), {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });

    } catch (error) {
        console.error('Text-to-speech error:', error);
        return new Response(JSON.stringify({
            error: {
                code: 'TTS_FAILED',
                message: error.message
            }
        }), {
            status: 500,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
    }
});

// Voice ID mapping for ElevenLabs
function getVoiceId(voiceName) {
    const voices = {
        'Rachel': '21m00Tcm4TlvDq8ikWAM',
        'Drew': '29vD33N1CtxCmqQRPOHJ',
        'Clyde': '2EiwWnXFnvU5JabPnv8n',
        'Paul': '5Q0t7uMcjvnagumLfvZi',
        'Domi': 'AZnzlk1XvdvUeBnXmlld',
        'Dave': 'CYw3kZ02Hs0563khs1Fj',
        'Fin': 'D38z5RcWu1voky8WS1ja',
        'Sarah': 'EXAVITQu4vr4xnSDxMaL',
        'Antoni': 'ErXwobaYiN019PkySvjV',
        'Thomas': 'GBv7mTt0atIp3Br8iCZE',
        'Charlie': 'IKne3meq5aSn9XLyUdCD',
        'Emily': 'LcfcDJNUP1GQjkzn1xUU',
        'Elli': 'MF3mGyEYCl7XYWbV9V6O',
        'Callum': 'N2lVS1w4EtoT3dr4eOWO',
        'Patrick': 'ODq5zmih8GrVes37Dizd',
        'Harry': 'SOYHLrjzK2X1ezoPC6cr',
        'Liam': 'TX3LPaxmHKxFdv7VOQHJ',
        'Dorothy': 'ThT5KcBeYPX3keUQqHPh',
        'Josh': 'TxGEqnHWrfWFTfGW9XjX',
        'Arnold': 'VR6AewLTigWG4xSOukaG',
        'Adam': 'pNInz6obpgDQGcFmaJgB',
        'Sam': 'yoZ06aMxZJJ28mfd3POQ'
    };
    
    return voices[voiceName] || voices['Rachel']; // Default to Rachel
}