-- ============================================================
-- Fluentify — Seed Data
-- Professional Contexts, Scenarios, Achievements, Node Categories
-- ============================================================

-- ============================================================
-- Professional Contexts with Scenario Templates
-- ============================================================
INSERT INTO professional_contexts (name, slug, vocabulary_tags, scenario_templates, icon_slug) VALUES
(
    'General',
    'general',
    ARRAY['everyday', 'travel', 'social', 'culture'],
    '[
        {"name": "Coffee Shop Chat", "description": "You are having a casual conversation at a coffee shop with a new acquaintance.", "ai_role": "Friendly barista and conversation partner", "difficulty": "A1"},
        {"name": "Travel Planning", "description": "You are at a travel agency planning your next vacation.", "ai_role": "Experienced travel agent", "difficulty": "A2"},
        {"name": "Job Interview", "description": "You are in a job interview for a position you really want.", "ai_role": "Professional HR interviewer", "difficulty": "B1"},
        {"name": "Apartment Hunting", "description": "You are meeting a landlord to see an apartment for rent.", "ai_role": "Property landlord showing the apartment", "difficulty": "A2"},
        {"name": "Restaurant Reservation", "description": "You are calling a restaurant to make a reservation for a special dinner.", "ai_role": "Restaurant host/hostess", "difficulty": "A1"}
    ]'::jsonb,
    'public'
),
(
    'Medicina',
    'medicina',
    ARRAY['anatomy', 'diagnosis', 'treatment', 'patient-care', 'pharmacy'],
    '[
        {"name": "Patient Consultation", "description": "A patient comes to your office describing symptoms. You need to take their medical history.", "ai_role": "Patient with flu-like symptoms", "difficulty": "B1"},
        {"name": "Emergency Room", "description": "You are an ER doctor receiving a patient with chest pain.", "ai_role": "Worried patient with chest pain", "difficulty": "B2"},
        {"name": "Medical Conference", "description": "You are presenting a case study at an international medical conference.", "ai_role": "Fellow doctor asking questions about your research", "difficulty": "C1"},
        {"name": "Pharmacy Consultation", "description": "A patient asks about medication interactions and side effects.", "ai_role": "Patient with multiple prescriptions", "difficulty": "B1"},
        {"name": "Telemedicine Call", "description": "You conduct a follow-up appointment via video call.", "ai_role": "Post-surgery patient checking in", "difficulty": "B1"}
    ]'::jsonb,
    'medical_services'
),
(
    'Ingeniería',
    'ingenieria',
    ARRAY['software', 'systems', 'architecture', 'debugging', 'agile'],
    '[
        {"name": "Sprint Planning", "description": "You are leading a sprint planning meeting with your international team.", "ai_role": "Senior developer proposing technical solutions", "difficulty": "B1"},
        {"name": "Code Review", "description": "You are reviewing code with a colleague and discussing best practices.", "ai_role": "Junior developer presenting their pull request", "difficulty": "B2"},
        {"name": "Client Demo", "description": "You are presenting a new feature to an important client.", "ai_role": "Client executive evaluating the product", "difficulty": "B2"},
        {"name": "Tech Interview", "description": "You are conducting a technical interview for a new team member.", "ai_role": "Candidate answering system design questions", "difficulty": "C1"},
        {"name": "Bug Report", "description": "You need to explain a critical production bug to your manager.", "ai_role": "Engineering manager asking for details", "difficulty": "B1"}
    ]'::jsonb,
    'engineering'
),
(
    'Finanzas',
    'finanzas',
    ARRAY['investment', 'banking', 'accounting', 'risk', 'markets'],
    '[
        {"name": "Investment Pitch", "description": "You are pitching an investment opportunity to a potential client.", "ai_role": "Wealthy client considering investment options", "difficulty": "B2"},
        {"name": "Budget Review", "description": "You are presenting the quarterly budget review to the board.", "ai_role": "Board member asking tough financial questions", "difficulty": "C1"},
        {"name": "Loan Consultation", "description": "A client comes to discuss mortgage options.", "ai_role": "First-time homebuyer seeking mortgage advice", "difficulty": "B1"},
        {"name": "Market Analysis", "description": "You are presenting market trends to your trading team.", "ai_role": "Trader asking about specific market indicators", "difficulty": "B2"},
        {"name": "Tax Advisory", "description": "A small business owner needs help with tax planning.", "ai_role": "Entrepreneur confused about tax obligations", "difficulty": "B1"}
    ]'::jsonb,
    'account_balance'
),
(
    'Videojuegos',
    'videojuegos',
    ARRAY['game-design', 'development', 'esports', 'streaming', 'community'],
    '[
        {"name": "Game Design Review", "description": "You are presenting your game design document to the creative team.", "ai_role": "Creative director giving feedback on your design", "difficulty": "B1"},
        {"name": "Esports Commentary", "description": "You are commentating a live esports match.", "ai_role": "Co-caster helping analyze the gameplay", "difficulty": "B2"},
        {"name": "Community Management", "description": "You are handling feedback from the game community on a new update.", "ai_role": "Passionate community member with concerns", "difficulty": "B1"},
        {"name": "Publisher Meeting", "description": "You are pitching your indie game to a publisher.", "ai_role": "Publisher evaluating your game for funding", "difficulty": "B2"},
        {"name": "QA Bug Triage", "description": "You are discussing critical bugs found during testing.", "ai_role": "QA tester reporting issues before launch", "difficulty": "B1"}
    ]'::jsonb,
    'sports_esports'
),
(
    'Turismo',
    'turismo',
    ARRAY['hospitality', 'travel', 'tourism', 'service', 'culture'],
    '[
        {"name": "Hotel Check-in", "description": "A guest arrives at your hotel and needs help with check-in.", "ai_role": "International tourist arriving at the hotel", "difficulty": "A2"},
        {"name": "City Tour Guide", "description": "You are giving a walking tour of the city to a group of tourists.", "ai_role": "Curious tourist asking about local history", "difficulty": "B1"},
        {"name": "Travel Emergency", "description": "A tourist has lost their passport and needs assistance.", "ai_role": "Distressed tourist who lost their passport", "difficulty": "B1"},
        {"name": "Restaurant Service", "description": "You are a waiter at an international restaurant.", "ai_role": "Diner asking about menu items and local cuisine", "difficulty": "A2"},
        {"name": "Tour Package Sales", "description": "You are selling vacation packages to potential clients.", "ai_role": "Couple looking for a romantic getaway", "difficulty": "B1"}
    ]'::jsonb,
    'flight_takeoff'
);

-- ============================================================
-- Node Categories
-- ============================================================
INSERT INTO node_categories (name, skill_area, color_hex) VALUES
('Gramática Básica', 'grammar', '#6C5CE7'),
('Gramática Intermedia', 'grammar', '#A29BFE'),
('Gramática Avanzada', 'grammar', '#4A3ABA'),
('Vocabulario General', 'vocabulary', '#00CEC9'),
('Vocabulario Profesional', 'vocabulary', '#55EFC4'),
('Fonética', 'phonetics', '#FD79A8'),
('Pronunciación', 'phonetics', '#E84393'),
('Escritura Kanji', 'writing', '#FDCB6E'),
('Escritura Cirílica', 'writing', '#E17055'),
('Cultura', 'culture', '#74B9FF'),
('Expresiones Idiomáticas', 'vocabulary', '#00B894');

-- ============================================================
-- Achievements
-- ============================================================
INSERT INTO achievements (slug, name, description, xp_reward, condition, icon_slug) VALUES
('first_session', 'Primera Sesión', 'Completa tu primera sesión de práctica', 50, '{"type": "session_count", "value": 1}', 'star'),
('five_sessions', 'Practicante', 'Completa 5 sesiones de práctica', 100, '{"type": "session_count", "value": 5}', 'local_fire_department'),
('twenty_sessions', 'Dedicado', 'Completa 20 sesiones de práctica', 250, '{"type": "session_count", "value": 20}', 'military_tech'),
('fifty_sessions', 'Veterano', 'Completa 50 sesiones de práctica', 500, '{"type": "session_count", "value": 50}', 'verified'),
('streak_3', 'En Racha', 'Mantén una racha de 3 días consecutivos', 75, '{"type": "streak", "value": 3}', 'whatshot'),
('streak_7', 'Semana Perfecta', 'Mantén una racha de 7 días consecutivos', 200, '{"type": "streak", "value": 7}', 'local_fire_department'),
('streak_30', 'Mes Imparable', 'Mantén una racha de 30 días consecutivos', 1000, '{"type": "streak", "value": 30}', 'emoji_events'),
('xp_500', 'Aventurero', 'Acumula 500 XP en total', 50, '{"type": "total_xp", "value": 500}', 'workspace_premium'),
('xp_5000', 'Artesano del Idioma', 'Acumula 5,000 XP en total', 200, '{"type": "total_xp", "value": 5000}', 'workspace_premium'),
('xp_25000', 'Sabio Lingüístico', 'Acumula 25,000 XP en total', 500, '{"type": "total_xp", "value": 25000}', 'emoji_events'),
('first_roleplay', 'Actor Novato', 'Completa tu primera sesión de Roleplay', 75, '{"type": "roleplay_count", "value": 1}', 'theater_comedy'),
('ten_roleplay', 'Actor de Método', 'Completa 10 sesiones de Roleplay', 300, '{"type": "roleplay_count", "value": 10}', 'theater_comedy'),
('first_whisper', 'Susurro Inicial', 'Completa tu primera sesión en Modo Susurro', 75, '{"type": "whisper_count", "value": 1}', 'mic'),
('ten_whisper', 'Voz Segura', 'Completa 10 sesiones en Modo Susurro', 300, '{"type": "whisper_count", "value": 10}', 'mic'),
('nodes_10', 'Explorador del Conocimiento', 'Domina 10 nodos de conocimiento', 150, '{"type": "mastered_nodes", "value": 10}', 'auto_awesome'),
('nodes_50', 'Constelación Brillante', 'Domina 50 nodos de conocimiento', 500, '{"type": "mastered_nodes", "value": 50}', 'stars');
