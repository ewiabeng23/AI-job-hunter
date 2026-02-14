-- Users
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    clerk_user_id VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    subscription_tier VARCHAR(20) DEFAULT 'free',
    applications_this_month INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- User CVs
CREATE TABLE user_cvs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    is_default BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Applications
CREATE TABLE applications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    job_title VARCHAR(255) NOT NULL,
    company VARCHAR(255) NOT NULL,
    job_url TEXT,
    match_score INTEGER,
    custom_cv TEXT,
    cover_letter TEXT,
    status VARCHAR(50) DEFAULT 'applied',
    applied_at TIMESTAMP DEFAULT NOW()
);
