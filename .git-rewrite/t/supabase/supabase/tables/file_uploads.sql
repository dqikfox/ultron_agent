CREATE TABLE file_uploads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID,
    filename VARCHAR(500),
    file_url TEXT,
    file_type VARCHAR(100),
    file_size INTEGER,
    processing_status VARCHAR(20) DEFAULT 'pending',
    processing_result TEXT,
    ocr_text TEXT,
    ai_analysis TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE
);