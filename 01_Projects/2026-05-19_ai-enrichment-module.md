---
title: IronHub AI Enrichment Module
date: 2026-05-19
status: active
tags: [ai, enrichment, meti, aws, spare-parts, technology, project]
---

# IronHub AI Enrichment Module

**Delivered by:** Micro Engineering Tech Inc. (METI)
**Delivery Date:** May 15, 2026
**Staging URL:** https://ironhub-platform-staging.ironhub.microengineering.ca/
**API Docs:** https://ironhub-backend-staging.ironhub.microengineering.ca/
**DB Docs:** https://dbdocs.io/hossam.taha/IronHub
**Google Drive Folder:** https://drive.google.com/drive/folders/1SuJ3W2JihBFcTD9jkMXVEkX7g1-HdpWg

## What It Does

The AI Enrichment Module transforms minimal input — a manufacturer and part number, an uploaded image, or a bulk spreadsheet — into complete, structured, and publish-ready IronHub listings. It combines layered data retrieval, multimodal AI processing, automatic categorization, and human-in-the-loop review to ensure accuracy, traceability, and consistency at marketplace scale.

## Delivered Capabilities (All 9 Confirmed Delivered)

| # | Deliverable | Description | Status |
|---|---|---|---|
| D1 | Bulk Enrichment Pipeline | End-to-end batch enrichment of Excel inputs (thousands of rows) with concurrent execution and scale-to-zero serverless processing | Delivered |
| D2 | Image-Based Enrichment | Processes user-uploaded images to extract identifying information and generate structured listings | Delivered |
| D3 | Image Retrieval | Automatically retrieves and attaches the most relevant product images to enriched listings | Delivered |
| D4 | IronHub Platform Integration | Enriched outputs fed directly into IronHub, including category synchronization and listing publishing | Delivered |
| D5 | Input Guardrails | Protective layer filtering malicious, irrelevant, or out-of-scope inputs before they reach the pipeline | Delivered |
| D6 | Human-in-the-Loop Review | Browser-based reviewer interface with field-level confidence scoring, editing, approval, and re-enrichment | Delivered |
| D7 | Automatic Categorization | AI-driven classification with automatic propagation of new categories into the IronHub platform | Delivered |
| D8 | AWS Cloud Deployment | Hybrid architecture: 24/7 app server (business logic, auth, jobs) + serverless scale-to-zero AI compute layer on AWS (RDS PostgreSQL + S3) | Delivered |
| D9 | Documentation Package | Deployment guide, API documentation, user guide, and operational procedures | Delivered |

## Technical Architecture

- **AI Model:** Gemini 3 Flash (selected after benchmarking for best accuracy/latency/cost balance)
- **Cloud:** Amazon Web Services (AWS)
- **Database:** Amazon RDS for PostgreSQL
- **File Storage:** Amazon S3 (OEM documents, datasheets, product images)
- **Architecture:** Hybrid — 24/7 app server for business logic + serverless scale-to-zero for AI compute
- **Cost Model:** AI compute scales to zero when idle — no standing cost for AI workload

## Accuracy Report (May 15, 2026)

**Overall Results:**
- Files evaluated: 28
- Total specifications validated: 322
- **True Positives (1.0): 253 (78.6%)**
- Partial TP (0.7): 48 (14.9%)
- False Positives (0.0): 21 (6.5%)
- **Simple file-average accuracy: 0.8532 (85.3%)**
- **Weighted accuracy: 0.8901 (89.0%)**

**Strengths:**
- Strong coverage of well-documented industrial product lines: Trico, Swagelok, Dwyer, Westlock, ACCU, Allen-Bradley
- Good interpretation of OEM model-code nomenclature
- Confidence calibration is broadly sensible — high-confidence-miss penalty triggered only on 21 of 322 specs

**Known Weaknesses:**
- Numeric weights are a consistent weak point (weight, viscosity, BOP chamber volumes)
- Product family confusion on similar part numbers (e.g., WypAll 35411 → X60 not X80)
- Niche/custom OEM parts with no public documentation (e.g., SEATRAX 40387 scored 0.0)
- Lubricant chemistry tables partly miscalibrated

**Recommended Next Steps (from METI):**
1. Add sanity check for numerical specs against manufacturer's own datasheet (not third-party distributors)
2. Disambiguate part numbers that map across multiple product families with a second lookup pass
3. Mark specs as 'tubing-' or 'system-dependent' instead of producing a definite value
4. When part number cannot be located in any OEM/distributor source, lower entire record's confidence
5. Calibrate units carefully (kg/lb conversion issues found)
6. Re-run failing records with stricter OEM-source-only retrieval and human review
7. Add automated cross-check rejecting any high-confidence numerical value disagreeing with sourced figure by >5%

## User Interface — 3 Input Modes

1. **Describe** — Free-text product description, optionally with an attached datasheet
2. **Images** — Upload product photos or nameplate images
3. **Spreadsheet** — Bulk Excel import (thousands of rows, concurrent processing)

**Navigation:** Home (launch jobs) → Results (all enriched listings) → Jobs (chronological history)

**Review Workflow:** Each enriched listing shows per-field confidence scores, source attribution, and editing tools. Reviewers can: Approve / Edit / Reject / Re-enrich.

## Cost Structure

- **Monthly support cost:** ~$5,000/month (from May 18 management meeting)
- **AI compute:** Scales to zero when idle — only pay when processing
- **Ongoing:** METI available for continued tuning, expansion of enrichment modalities, and further integration

## Related Notes

- [[2026-05-11_spare-parts-enrichment-tool]] — Original project note for this initiative
- [[ironhub-company]] — IronHub company context
- [[2026-05-18_meeting-ironhub-management-update]] — Management meeting where $5K/month support cost discussed
- [[2026-05-19_meeting-suncor-ironhub-notes]] — Suncor meeting where AI tool was referenced
- [[2026-05-19_cenovus-ai-enrichment-engagement]] — Cenovus engagement using this tool
