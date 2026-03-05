SELECT 
    text_content, 
    source_file, 
    data_type, 
    1 - (embedding <=> :embedding) AS score
FROM fastapi_vectorized
ORDER BY score DESC
LIMIT :limit;