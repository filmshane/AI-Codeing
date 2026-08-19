-- FPI CRM schema v3
-- Locked statuses (pipeline stage)
-- NEW_LISA_LEAD → APPROVED_LEAD_SENDING_ALEX → CURR_ALEX
--   → SCOUTING_LEAD → WAITING_MAX_PRICE_SHANE → ALEX_MANAGING
--   → CLIENT_APPROVED_CONTRACT_PENDING → CONTRACT_SIGNED
--   → FINDING_FLIPPER → ASSIGNED_TO_FLIPPER → CLOSED
-- Terminal: SUPPRESSED | DISQUALIFIED | DEAD | NURTURE

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS schema_meta (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS leads (
  id TEXT PRIMARY KEY,

  -- Identity / contact
  full_name TEXT,
  first_name TEXT,
  last_name TEXT,
  phones_json TEXT DEFAULT '[]',
  emails_json TEXT DEFAULT '[]',
  preferred_contact TEXT,          -- sms|email|phone
  best_time_to_call TEXT,
  timezone TEXT DEFAULT 'America/New_York',

  -- Property
  property_address TEXT,
  property_city TEXT,
  property_state TEXT,
  property_zip TEXT,
  property_lat REAL,
  property_lon REAL,
  property_type TEXT,
  beds REAL,
  baths REAL,
  sqft REAL,
  year_built INTEGER,
  occupancy TEXT,
  condition_notes TEXT,
  phone_primary TEXT,
  email_primary TEXT,
  garage_type TEXT,                 -- none|attached|detached|carport|unknown
  garage_spaces REAL,
  lot_size_acres REAL,
  lot_size_sqft REAL,
  stories REAL,
  basement_type TEXT,               -- none|unfinished|partial|finished|unknown
  last_remodel_year INTEGER,
  last_remodel_notes TEXT,
  roof_age_or_condition TEXT,
  hvac_age_or_condition TEXT,
  major_repairs_needed TEXT,
  hoa TEXT,
  pool TEXT,
  tenant_lease_end TEXT,
  listed_with_agent TEXT,
  other_offers TEXT,
  house_info_summary TEXT,

  -- Lisa / source
  source_platform TEXT,            -- craigslist|fb|zillow|website|atlas|other
  source_ad_url TEXT,
  source_ad_title TEXT,
  source_ad_body TEXT,
  source_posted_at TEXT,
  source_price_ask REAL,
  lisa_notes TEXT,
  marketing_email_sent_at TEXT,
  marketing_sms_sent_at TEXT,
  website_link_sent_at TEXT,

  -- Website / opt-in
  website_hit_at TEXT,
  website_opt_in INTEGER DEFAULT 0,
  website_opt_in_at TEXT,
  ai_call_consent INTEGER DEFAULT 0,
  ai_call_consent_text TEXT,
  ai_call_consent_at TEXT,
  chatbot_transcript_json TEXT,
  preferred_call_window TEXT,      -- "short_call_now" | datetime ISO | free text
  available_for_short_call INTEGER DEFAULT 0,

  -- Alex qualify
  qualified TEXT,                  -- Y | N | NULL
  qualified_at TEXT,
  qualified_by TEXT,
  motivation TEXT,
  motivation_detail TEXT,
  timeline TEXT,
  walk_away_ask REAL,
  mortgage_balance_approx REAL,
  owner_authority_notes TEXT,
  alex_notes TEXT,
  appointment_at TEXT,

  -- Stage
  status TEXT NOT NULL DEFAULT 'NEW_LISA_LEAD',
  owner_agent TEXT,                -- lisa|alex|scout|shane|ryan|blake|human
  stage_entered_at TEXT,
  do_not_contact INTEGER DEFAULT 0,
  dnc_reason TEXT,

  -- Scout package
  scout_status TEXT,
  scout_package_path TEXT,
  scout_arv_working REAL,
  scout_arv_low REAL,
  scout_arv_high REAL,
  scout_rehab_low REAL,
  scout_rehab_medium REAL,
  scout_rehab_high REAL,
  scout_mao_flip_low REAL,
  scout_mao_flip_medium REAL,
  scout_mao_flip_high REAL,
  scout_seller_max_low REAL,
  scout_seller_max_medium REAL,
  scout_seller_max_high REAL,
  scout_assignment_fee REAL DEFAULT 15000,
  scout_deal_works_medium INTEGER,
  scout_recap_json TEXT,

  -- Shane max
  max_price REAL,
  max_price_set_at TEXT,
  max_price_set_by TEXT,
  underwriting_case TEXT,          -- low|medium|high

  -- Contract / Ryan-Alex manage
  contract_status TEXT,
  contract_sent_at TEXT,
  contract_signed_at TEXT,
  contract_reminder_28h_at TEXT,
  client_approved_contract_at TEXT,

  -- Dispo / flipper
  flipper_status TEXT,
  flipper_target_price REAL,
  assigned_flipper_id TEXT,
  assigned_flipper_name TEXT,
  assignment_fee_actual REAL,

  -- Meta
  utm_campaign TEXT,
  notes TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS outreach_messages (
  id TEXT PRIMARY KEY,
  lead_id TEXT NOT NULL REFERENCES leads(id),
  channel TEXT NOT NULL,            -- sms|email|chat|voice
  direction TEXT DEFAULT 'out',    -- out|in
  template_id TEXT,
  subject TEXT,
  body TEXT NOT NULL,
  to_address TEXT,
  from_address TEXT,
  provider_id TEXT,
  status TEXT,
  sent_at TEXT,
  personalization_json TEXT,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS activities (
  id TEXT PRIMARY KEY,
  lead_id TEXT NOT NULL REFERENCES leads(id),
  actor TEXT NOT NULL,
  type TEXT NOT NULL,
  payload_json TEXT,
  at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ad_sources (
  id TEXT PRIMARY KEY,
  platform TEXT NOT NULL,
  monitor_url_or_query TEXT,
  geo TEXT,
  enabled INTEGER DEFAULT 1,
  last_scan_at TEXT,
  notes TEXT
);

CREATE TABLE IF NOT EXISTS scout_runs (
  id TEXT PRIMARY KEY,
  lead_id TEXT NOT NULL REFERENCES leads(id),
  package_json TEXT NOT NULL,
  package_path TEXT,
  status TEXT,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS appointments (
  id TEXT PRIMARY KEY,
  lead_id TEXT NOT NULL REFERENCES leads(id),
  agent TEXT NOT NULL,
  starts_at TEXT NOT NULL,
  timezone TEXT,
  status TEXT,
  notes TEXT,
  created_at TEXT NOT NULL
);

-- Cash buyers / flippers (Blake research)
CREATE TABLE IF NOT EXISTS flippers (
  id TEXT PRIMARY KEY,
  company_name TEXT,
  contact_name TEXT,
  phones_json TEXT DEFAULT '[]',
  emails_json TEXT DEFAULT '[]',
  website TEXT,
  markets_json TEXT DEFAULT '[]',  -- ["Chattanooga","Cleveland TN"]
  source_url TEXT,
  source_type TEXT,                -- zillow_investor|restore_co|fb_group|website|list|other
  buys_as_is INTEGER DEFAULT 1,
  has_repair_arm INTEGER DEFAULT 0,
  notes TEXT,
  last_researched_at TEXT,
  active INTEGER DEFAULT 1,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS flipper_touches (
  id TEXT PRIMARY KEY,
  flipper_id TEXT NOT NULL REFERENCES flippers(id),
  lead_id TEXT REFERENCES leads(id),
  channel TEXT,
  body TEXT,
  status TEXT,
  at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS status_history (
  id TEXT PRIMARY KEY,
  lead_id TEXT NOT NULL REFERENCES leads(id),
  from_status TEXT,
  to_status TEXT NOT NULL,
  actor TEXT,
  at TEXT NOT NULL,
  note TEXT
);

CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
CREATE INDEX IF NOT EXISTS idx_leads_qualified ON leads(qualified);
CREATE INDEX IF NOT EXISTS idx_leads_address ON leads(property_address);
CREATE INDEX IF NOT EXISTS idx_activities_lead ON activities(lead_id, at);
CREATE INDEX IF NOT EXISTS idx_outreach_lead ON outreach_messages(lead_id);
CREATE INDEX IF NOT EXISTS idx_flippers_active ON flippers(active);
CREATE INDEX IF NOT EXISTS idx_status_hist_lead ON status_history(lead_id, at);

INSERT OR REPLACE INTO schema_meta(key, value) VALUES ('version', '3');
INSERT OR REPLACE INTO schema_meta(key, value) VALUES ('locked_at', datetime('now'));
