-- Halal Seoul scanlog_db schema v1
-- PostgreSQL 15+

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE halal_ingredients (
  ingredient_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  canonical_name TEXT UNIQUE NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('halal', 'haram', 'mashbooh', 'unknown')),
  confidence_score NUMERIC(4,3) CHECK (confidence_score >= 0 AND confidence_score <= 1),
  reason_template TEXT,
  source_title TEXT,
  source_url TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_halal_ingredients_status ON halal_ingredients(status);

CREATE TABLE scan_sessions (
  scan_session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  success BOOLEAN NOT NULL,
  lang TEXT NOT NULL DEFAULT 'en',
  ocr_engine TEXT NOT NULL DEFAULT 'google_vision',
  ocr_attempt_count INTEGER NOT NULL DEFAULT 1 CHECK (ocr_attempt_count >= 1 AND ocr_attempt_count <= 5),
  ingredient_count INTEGER NOT NULL DEFAULT 0 CHECK (ingredient_count >= 0),
  overall_risk TEXT NOT NULL CHECK (overall_risk IN ('halal', 'haram', 'mashbooh', 'unknown')),
  latency_ms INTEGER NOT NULL CHECK (latency_ms >= 0),
  raw_ocr_text TEXT,
  trace_id TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_scan_sessions_user_created ON scan_sessions(user_id, created_at DESC);
CREATE INDEX idx_scan_sessions_success ON scan_sessions(success);
CREATE INDEX idx_scan_sessions_created ON scan_sessions(created_at DESC);

CREATE TABLE ingredient_results (
  ingredient_result_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  scan_session_id UUID NOT NULL REFERENCES scan_sessions(scan_session_id) ON DELETE CASCADE,
  raw_text TEXT NOT NULL,
  normalized_text TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('halal', 'haram', 'mashbooh', 'unknown')),
  confidence NUMERIC(4,3) CHECK (confidence >= 0 AND confidence <= 1),
  reason TEXT,
  source_title TEXT,
  source_url TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_ingredient_results_session ON ingredient_results(scan_session_id);
CREATE INDEX idx_ingredient_results_status ON ingredient_results(status);

CREATE TABLE misclassification_reports (
  report_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  scan_session_id UUID NOT NULL REFERENCES scan_sessions(scan_session_id) ON DELETE CASCADE,
  ingredient_result_id UUID REFERENCES ingredient_results(ingredient_result_id) ON DELETE SET NULL,
  reporter_user_id UUID NOT NULL,
  current_status TEXT NOT NULL CHECK (current_status IN ('received', 'reviewing', 'resolved', 'rejected')),
  requested_status TEXT CHECK (requested_status IN ('halal', 'haram', 'mashbooh', 'unknown')),
  reason TEXT NOT NULL,
  admin_note TEXT,
  reviewed_by UUID,
  reviewed_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_reports_status_created ON misclassification_reports(current_status, created_at DESC);
