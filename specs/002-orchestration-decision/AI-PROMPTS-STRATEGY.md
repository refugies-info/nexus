# AI Prompts Strategy

**Date**: 2025-10-21
**Context**: Nexus pipeline stages requiring LLM processing for data enrichment and transformation
**Approach**: Structured prompts with quality thresholds and cost optimization

---

## Overview

The Nexus pipeline uses AI (LLM) processing in three stages:
1. **Enrichment**: Enhance service descriptions and metadata
2. **Langage Clair**: Simplify French text for accessibility
3. **Translation**: Translate to other languages (English, Arabic, etc.)

This document specifies prompts, quality thresholds, and model selection for each stage.

---

## Stage 1: Enrichment

### Purpose
Enhance service data with additional context, improve descriptions, and fill missing fields.

### Prompt Template

```
You are a French social services data specialist. Enhance the following service record
with additional context and improved descriptions.

Service Data:
{
  "nom": "{service_name}",
  "description": "{service_description}",
  "publics": {publics_list},
  "conditions_acces": "{access_conditions}",
  "frais": "{cost_info}",
  "adresse": "{address}",
  "telephone": "{phone}",
  "courriel": "{email}",
  "horaires": "{hours}"
}

Tasks:
1. Improve the description to be more comprehensive (100-200 words)
2. Add missing context about eligibility criteria
3. Clarify access methods and requirements
4. Ensure all critical fields are complete

Output Format (JSON):
{
  "enriched_description": "...",
  "enriched_conditions_acces": "...",
  "enriched_publics": [...],
  "confidence_score": 0.0-1.0,
  "missing_fields": [...],
  "notes": "..."
}

Constraints:
- Maintain factual accuracy (do not invent information)
- Use professional French language
- Keep descriptions under 2000 characters
- Confidence score: 1.0 = high confidence, 0.0 = low confidence
```

### Quality Thresholds

| Metric | Threshold | Action |
|--------|-----------|--------|
| **Confidence Score** | < 0.6 | Flag for manual review |
| **Missing Fields** | > 2 | Flag for manual review |
| **Description Length** | > 2000 chars | Truncate and flag |
| **Language Quality** | Grammar errors | Flag for manual review |

### Model Selection
- **Primary**: GPT-4 (better quality, higher cost)
- **Fallback**: GPT-3.5-turbo (faster, lower cost)
- **Fast Mode** (catch-up): GPT-3.5-turbo (lower quality threshold acceptable)

### Cost Estimate
- **GPT-4**: ~$0.03-0.05 per enrichment
- **GPT-3.5-turbo**: ~$0.01-0.02 per enrichment
- **Monthly** (100 services): $1-5 (GPT-3.5) or $3-5 (GPT-4)

---

## Stage 2: Langage Clair (Plain Language Simplification)

### Purpose
Simplify French text to be accessible to people with lower literacy levels, refugees, and non-native speakers.

### Prompt Template

```
You are a French language accessibility specialist. Simplify the following text
to be understandable by people with basic French literacy (A2-B1 level).

Original Text:
"{original_text}"

Guidelines:
1. Use simple, common French words (avoid technical jargon)
2. Keep sentences short (max 15 words per sentence)
3. Use active voice when possible
4. Explain acronyms and abbreviations
5. Break complex ideas into smaller parts
6. Maintain factual accuracy
7. Keep the same meaning and tone

Output Format (JSON):
{
  "simplified_text": "...",
  "readability_score": 0.0-1.0,
  "changes_made": [...],
  "confidence_score": 0.0-1.0,
  "notes": "..."
}

Readability Score:
- 1.0 = Very easy (A1 level)
- 0.75 = Easy (A2 level)
- 0.5 = Moderate (B1 level)
- 0.25 = Difficult (B2+ level)
- 0.0 = Too complex
```

### Quality Thresholds

| Metric | Threshold | Action |
|--------|-----------|--------|
| **Readability Score** | < 0.5 | Flag for manual review |
| **Confidence Score** | < 0.7 | Flag for manual review |
| **Text Length Change** | > 50% longer | Flag for review |
| **Meaning Preservation** | Detected loss | Flag for manual review |

### Model Selection
- **Primary**: GPT-4 (better language understanding)
- **Fallback**: GPT-3.5-turbo (acceptable for simple texts)
- **Fast Mode** (catch-up): GPT-3.5-turbo

### Cost Estimate
- **GPT-4**: ~$0.02-0.04 per simplification
- **GPT-3.5-turbo**: ~$0.01-0.02 per simplification
- **Monthly** (100 services): $1-2 (GPT-3.5) or $2-4 (GPT-4)

---

## Stage 3: Translation

### Purpose
Translate service descriptions and key information to multiple languages (English, Arabic, Spanish, etc.).

### Prompt Template

```
You are a professional translator specializing in social services documentation.
Translate the following French text to {target_language} while maintaining accuracy
and cultural appropriateness for refugees and immigrants.

Original French Text:
"{french_text}"

Target Language: {target_language}
Context: Social service for refugees/immigrants in France

Requirements:
1. Maintain factual accuracy
2. Use culturally appropriate terminology
3. Preserve formatting and structure
4. Translate acronyms appropriately (or explain in target language)
5. Ensure readability for non-native speakers
6. Keep tone professional and welcoming

Output Format (JSON):
{
  "translated_text": "...",
  "target_language": "{target_language}",
  "terminology_notes": {...},
  "confidence_score": 0.0-1.0,
  "cultural_notes": "...",
  "notes": "..."
}

Confidence Score:
- 1.0 = Professional quality, ready to publish
- 0.75 = Good quality, minor review recommended
- 0.5 = Acceptable, manual review recommended
- 0.25 = Poor quality, requires manual revision
- 0.0 = Unusable
```

### Quality Thresholds

| Metric | Threshold | Action |
|--------|-----------|--------|
| **Confidence Score** | < 0.7 | Flag for manual review |
| **Terminology Issues** | > 2 | Flag for manual review |
| **Cultural Concerns** | Any noted | Flag for manual review |
| **Length Variance** | > 30% from original | Flag for review |

### Supported Languages (Phase 1)
- English
- Arabic
- Spanish

### Supported Languages (Phase 2+)
- German
- Italian
- Portuguese
- Somali
- Tigrinya
- Ukrainian

### Model Selection
- **Primary**: GPT-4 (better translation quality)
- **Fallback**: GPT-3.5-turbo (acceptable for simple texts)
- **Fast Mode** (catch-up): GPT-3.5-turbo

### Cost Estimate
- **GPT-4**: ~$0.03-0.05 per translation
- **GPT-3.5-turbo**: ~$0.01-0.02 per translation
- **Monthly** (100 services × 3 languages): $3-15 (GPT-3.5) or $9-15 (GPT-4)

---

## Fast Mode vs Normal Mode

### Fast Mode (Smart Catch-Up)
Used when processing updates to existing records (no human review during catch-up).

**Characteristics**:
- Uses GPT-3.5-turbo (faster, lower cost)
- Lower quality thresholds (0.5 instead of 0.7)
- No manual review during catch-up
- Diff review happens after catch-up completes

**Quality Thresholds**:
- Enrichment: confidence > 0.5
- Langage Clair: readability > 0.4
- Translation: confidence > 0.5

### Normal Mode (New Programs)
Used when processing new programs through the full pipeline.

**Characteristics**:
- Uses GPT-4 (higher quality)
- Higher quality thresholds (0.7+)
- Manual review at each stage
- Iterative refinement possible

**Quality Thresholds**:
- Enrichment: confidence > 0.7
- Langage Clair: readability > 0.6
- Translation: confidence > 0.8

---

## Cost Optimization Strategies

### Strategy 1: Batch Processing
Process multiple services together to reduce API calls.

```python
# Instead of:
for service in services:
    result = openai.ChatCompletion.create(...)  # 100 calls

# Do this:
batch_prompt = f"Process these {len(services)} services..."
result = openai.ChatCompletion.create(...)  # 1 call
```

**Savings**: ~50-70% reduction in API calls

### Strategy 2: Caching
Cache results for identical inputs (same service, same language).

```python
cache_key = hash(f"{service_id}_{language}_{stage}")
if cache_key in redis:
    return redis.get(cache_key)
```

**Savings**: ~20-30% reduction for repeated translations

### Strategy 3: Model Selection
Use GPT-3.5-turbo for fast mode, GPT-4 only for new programs.

**Savings**: ~60% reduction in costs (GPT-3.5 is 3-5x cheaper)

### Strategy 4: Prompt Optimization
Use shorter, more specific prompts to reduce token usage.

**Savings**: ~10-20% reduction in tokens per request

---

## Monitoring & Quality Assurance

### Metrics to Track
- **Confidence scores** (per stage, per model)
- **Quality threshold violations** (% flagged for review)
- **Cost per service** (by stage, by model)
- **Processing time** (by stage, by model)
- **User satisfaction** (editorial team feedback)

### Monitoring Dashboard
Track in Supabase:
```sql
CREATE TABLE ai_processing_metrics (
  id UUID PRIMARY KEY,
  stage TEXT,
  model TEXT,
  confidence_score FLOAT,
  quality_threshold FLOAT,
  processing_time_ms INT,
  cost_cents INT,
  flagged_for_review BOOLEAN,
  created_at TIMESTAMPTZ
);
```

### Feedback Loop
- Editorial team rates AI output quality
- Adjust thresholds based on feedback
- Retrain prompts quarterly
- A/B test model improvements

---

## Implementation Tasks

### Phase 1 (Weeks 9-11)
- **T050**: Implement enrichment prompt + GPT-3.5-turbo integration
- **T051**: Implement langage_clair prompt + GPT-3.5-turbo integration
- **T052**: Implement translation prompt + GPT-3.5-turbo integration
- **T053**: Add quality threshold validation
- **T054**: Add monitoring metrics

### Phase 2 (Weeks 12-15)
- **T055**: Upgrade to GPT-4 for normal mode
- **T056**: Implement batch processing optimization
- **T057**: Implement caching layer (Redis)
- **T058**: Add cost tracking dashboard
- **T059**: Implement feedback loop

### Phase 3 (Months 4-6)
- **T060**: Fine-tune prompts based on feedback
- **T061**: Implement model selection logic (GPT-4 vs 3.5)
- **T062**: Add A/B testing framework
- **T063**: Implement cost optimization strategies

---

## Error Handling

### API Failures
```python
# Retry with exponential backoff
@retry(max_attempts=3, backoff_factor=2)
def call_openai_api(prompt):
    try:
        return openai.ChatCompletion.create(...)
    except RateLimitError:
        raise  # Retry
    except APIError:
        raise  # Retry
    except Exception as e:
        log_error(e)
        return None  # Flag for manual review
```

### Quality Failures
```python
# If confidence < threshold, flag for manual review
if result.confidence_score < QUALITY_THRESHOLD:
    flag_for_manual_review(service_id, stage, reason="low_confidence")
    return None  # Don't apply result
```

### Cost Control
```python
# Track costs, alert if exceeding budget
monthly_cost = sum(metrics.cost_cents) / 100
if monthly_cost > MONTHLY_BUDGET:
    alert_team("AI processing budget exceeded")
    switch_to_gpt35_turbo()
```

---

## References

- [OpenAI API Documentation](https://platform.openai.com/docs)
- [GPT-4 vs GPT-3.5 Comparison](https://platform.openai.com/docs/models/gpt-4)
- [Prompt Engineering Best Practices](https://platform.openai.com/docs/guides/prompt-engineering)
- [Token Counting](https://platform.openai.com/tokenizer)
