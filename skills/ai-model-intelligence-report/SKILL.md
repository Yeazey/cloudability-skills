---
name: ai-model-intelligence-report
description: Use when the user asks for an "AI model report", "AI model intelligence report", "show AI spend by model", or wants to understand how their cloud AI model spending compares to quality benchmarks. Pulls AI model spend from Cloudability and enriches it with Artificial Analysis benchmark context (quality index, price tier, input/output ratio, and efficiency verdict).
---

# AI Model Intelligence Report

Produce a single-page HTML report that maps the active customer's Cloudability AI model spend
against Artificial Analysis benchmark data — quality index, price tier, token I/O ratio, and
a per-model efficiency verdict.

---

## Step 0 — Load Customer Context

Before any data calls, read `.bob/active-customer.json` if it exists. Extract:
- `name` / `display_name` — used in the report header
- `branding` — use `primary_color`, `secondary_color`, `font_stack` for HTML styling if set;
  fall back to generic defaults (`#0068b5`, `#7c5cd8`, system-ui) if not set
- `checkin_context.ai_service_filter` — custom Bedrock/AI service filter if set;
  default filter is `service_name=@Bedrock`

---

## Step 0b — Discover AI Dimension Names

**AI Model and AI Model Family dimension names vary by customer** — never assume they are
`category4` or `category12`. Always resolve the correct dimension key at runtime.

Call `list_cost_measures` (no parameters needed). Scan the returned dimensions list and find:
- The dimension whose **label** is exactly `"AI Model"` → store its `name` as `$dim_ai_model`
- The dimension whose **label** is exactly `"AI Model Family"` → store its `name` as `$dim_ai_family`
- The dimension whose **label** is exactly `"Token Type"` (or contains "token type") → store as `$dim_token_type`

If `"AI Model Family"` is not found, set `$dim_ai_family = null` and skip any family-level queries.
If `"Token Type"` is not found, set `$dim_token_type = null` and skip the I/O ratio breakdown.

Use these resolved dimension names (`$dim_ai_model`, `$dim_ai_family`, `$dim_token_type`) in
**every subsequent `run_cost_report` call** — never substitute `category4`, `category5`, or
`category12` directly.

---

## Step 1 — Ask for Date Range

Ask the user which time window to use:

> "Which date range would you like for the AI model report?"
> - Last 7 days
> - Last 30 days (recommended)
> - Last 90 days
> - Custom range (YYYY-MM-DD to YYYY-MM-DD)

Wait for their reply before proceeding.

---

## Step 2 — Fetch AI Model Spend

### 2a. Spend by model

Call `run_cost_report` with:
- `dimensions`: `$dim_ai_model`
- `filters`: `["<ai_service_filter>", "$dim_ai_model!=(not set)"]`
  where `<ai_service_filter>` is from customer context or defaults to `service_name=@Bedrock`
- `metrics`: `unblended_cost`
- `sort`: `unblended_costDESC`
- `limit`: 50
- `start_date` / `end_date`: from Step 1

### 2b. Token type breakdown (AI Model + Token Type)

Only run this query if `$dim_token_type` was resolved in Step 0b.

Call `run_cost_report` with the same filters but:
- `dimensions`: `$dim_ai_model,$dim_token_type`
- `limit`: 100

This gives the input/output token split per model, used to compute the I/O ratio column.

### 2c. AI Model Family breakdown (optional)

Only run this query if `$dim_ai_family` was resolved in Step 0b AND has real values
(i.e. not all `(not set)`).

Call `run_cost_report` with:
- `dimensions`: `$dim_ai_family`
- same filters as 2a but replace model dimension filter with `$dim_ai_family!=(not set)`
- `metrics`: `unblended_cost`
- `sort`: `unblended_costDESC`

Use the family results for the AI family bar chart in the HTML report if available.
If all values are `(not set)`, derive families from model names in Step 3 instead and show
an amber notice: "AI Model Family dimension is still processing — families derived from model names."

### 2d. Total AI spend (for % share column)

Sum all `unblended_cost` values from 2a result. This is the denominator for the `Spend %` column.

---

## Step 3 — Enrich with Artificial Analysis Benchmark Data

Map each model value from `$dim_ai_model` to its Artificial Analysis profile using naming context.

### Matching rules

1. **Try exact match first** — check if the model value appears verbatim in the mapping table below
   (e.g. `claude opus 4.8` matches exactly).
2. **Try version-prefix match** — strip the trailing minor version and match the prefix
   (e.g. `claude opus 4.8` → check `claude opus 4.x` row).
3. **Fall back to family match** — match the family name prefix only
   (e.g. `claude opus` → Anthropic Opus family).
4. **Unknown models** — mark AA Match as `Unknown`, Quality Index as `—`, and apply
   best-effort price tier from context clues (provider name, model size). Mark all estimated
   fields with `(est.)`.

The AA Match column in the report must use the **exact name shown on artificialanalysis.ai**
(e.g. "Claude Opus 4.8", not "Claude Opus 4 (latest)"). Never substitute a generic family label
when a specific version match exists.

### Mapping reference — Anthropic Claude

| AI Model value | AA Model Name (exact) | Quality Index | Price Tier | Use Case |
|---|---|---|---|---|
| `claude opus 4.8` | Claude Opus 4.8 | ~88 / Top | Premium ($15/$75 /Mtok) | Anthropic's most capable model as of mid-2026. Designed for the most complex reasoning, long-document analysis, advanced coding, and agentic multi-step tasks. Excels at tasks requiring deep synthesis and judgment. |
| `claude opus 4.7` | Claude Opus 4.7 | ~87 / Top | Premium ($15/$75 /Mtok) | Near-identical to 4.8 in capability; prior minor release. Suitable for the same frontier use cases — complex reasoning, research synthesis, long-context processing. |
| `claude opus 4.6` | Claude Opus 4.6 | ~86 / Top | Premium ($15/$75 /Mtok) | Earlier Opus 4 minor. Strong reasoning and instruction-following. Same premium tier; typically displaced by 4.7/4.8 in production. |
| `claude opus 4.5` | Claude Opus 4.5 | ~84 / Top | Premium ($15/$75 /Mtok) | First Opus 4 release. Established the Opus 4 quality bar. Appropriate for complex agentic workflows and nuanced long-form generation. |
| `claude opus 4.1` | Claude Opus 4.1 | ~83 / Top | Premium ($15/$75 /Mtok) | Transitional Opus 4 minor. Comparable to 4.5 in most benchmarks. |
| `claude opus 3.*` / `claude opus 3` | Claude Opus 3 | ~78 / High | High ($15/$75 /Mtok legacy) | Previous Opus generation. Strong reasoning but now outclassed by Sonnet 4.x on price/quality. Use only if Opus 3 is required by a specific integration. |
| `claude sonnet 5` | Claude Sonnet 5 | ~80 / High | Mid ($3/$15 /Mtok) | Next-generation Sonnet; strong balanced model for coding assist, document Q&A, and conversational agents. Excellent price-to-quality ratio for production workloads. |
| `claude sonnet 4.6` | Claude Sonnet 4.6 | ~79 / High | Mid ($3/$15 /Mtok) | High-capability balanced model. Well-suited for coding, summarisation, RAG pipelines, and interactive agents. AA rates it near the top of the mid-tier. |
| `claude sonnet 4.5` | Claude Sonnet 4.5 | ~78 / High | Mid ($3/$15 /Mtok) | Workhorse Sonnet for enterprise workloads. Handles complex instructions, multi-turn dialogue, and structured data extraction efficiently. |
| `claude sonnet 4` / `claude sonnet 4.0` | Claude Sonnet 4 | ~74 / High | Mid ($3/$15 /Mtok) | Earlier Sonnet 4 release. Solid mid-tier model for summarisation, classification, and Q&A. |
| `claude sonnet 3.*` | Claude Sonnet 3.x | ~72 / High | Mid ($3/$15 /Mtok) | Previous Sonnet generation. Still capable; best suited for structured tasks and high-volume summarisation. |
| `claude haiku 4.5` | Claude Haiku 4.5 | ~69 / Mid | Low ($0.25/$1.25 /Mtok) | Fast, lightweight model for high-throughput tasks: content moderation, intent classification, short-form extraction, and chatbot routing. AA's lowest-cost Anthropic option. |
| `claude haiku 3.5` | Claude Haiku 3.5 | ~66 / Mid | Low ($0.25/$1.25 /Mtok) | Previous Haiku generation. Good for simple classification and low-latency applications at scale. |
| `claude fable*` | Claude Fable (experimental) | ~70 / Mid (est.) | Mid (est.) | Experimental/fine-tuned Claude variant; not yet on AA's main leaderboard. Likely optimised for a specific creative or structured task domain. Monitor usage and validate against Sonnet. |
| `claude mythos*` | Claude Mythos | ~78 / High (est.) | Mid-High (est.) | Anthropic's long-form narrative and creative model. Optimised for story generation, extended prose, and creative writing tasks. Not yet on AA's main inference leaderboard — blurb from published model card. |

### Mapping reference — OpenAI GPT

| AI Model value | AA Model Name (exact) | Quality Index | Price Tier | Use Case |
|---|---|---|---|---|
| `gpt5.5` / `gpt-5.5` | GPT-5.5 | ~87 / Top | Premium ($15/$60 /Mtok) | OpenAI's frontier reasoning model. Designed for complex problem-solving, advanced code generation, scientific reasoning, and long-context tasks. Comparable to Claude Opus 4.x in capability. |
| `gpt5.4` / `gpt-5.4` | GPT-5.4 | ~85 / Top | Premium ($10/$30 /Mtok) | High-capability GPT-5 variant. Strong for agentic pipelines, code review, and multi-step reasoning. Slightly lower price point than 5.5. |
| `gpt5` / `gpt-5` | GPT-5 | ~86 / Top | Premium ($10/$30 /Mtok) | Base GPT-5 release. Top-tier reasoning and instruction-following. Suitable for the most demanding OpenAI-based workloads. |
| `gpt4.*` / `gpt-4o*` / `gpt4o` | GPT-4o / GPT-4.1 | ~80 / High | High ($2.50/$10 /Mtok) | Flagship previous-gen GPT. Efficient for coding, structured data, and conversational tasks. Still a strong choice for workloads that don't need GPT-5 capability. |
| `gpt-oss-120b` | GPT OSS 120B | ~72 / High (est.) | Low (est.) | Large open-weight GPT-family model. Suitable for high-volume batch processing where output quality must exceed smaller models. |
| `gpt-oss-20b` | GPT OSS 20B | ~64 / Mid (est.) | Very Low (est.) | Smaller open-weight GPT-family model. Good for classification, routing, and lightweight extraction at scale. |

### Mapping reference — Google Gemini

| AI Model value | AA Model Name (exact) | Quality Index | Price Tier | Use Case |
|---|---|---|---|---|
| `gemini 3.5*` | Gemini 3.5 | ~92 / Top (est.) | Premium (est.) | Latest Gemini frontier model. Cutting-edge multimodal performance across reasoning, code, and vision. |
| `gemini 3.1*` | Gemini 3.1 | ~89 / Top (est.) | Premium (est.) | Balanced Gemini 3 variant with strong enterprise task performance. |
| `gemini 3 pro*` | Gemini 3 Pro | ~88 / Top (est.) | High (est.) | Pro-tier Gemini 3 optimised for coding, analysis, and structured reasoning. |
| `gemini 3*` | Gemini 3 | ~87 / Top (est.) | High (est.) | Next-generation multimodal model; advanced reasoning and code generation. |
| `gemini 2.5 pro*` | Gemini 2.5 Pro | ~85 / Top | High ($3.50/$10.50 /Mtok) | Google's flagship reasoning model. Excels at code, math, and long-context document analysis. Competitive price for Top-tier quality. |
| `gemini 2.5*` | Gemini 2.5 | ~82 / High | Mid ($1.25/$5 /Mtok) | Efficient Gemini 2.5 variant. Strong multimodal and document reasoning at mid-tier pricing. |
| `gemini 2.*` / `gemini-2*` | Gemini 2.0 Pro / Flash | ~83 / Top | Mid ($1.25/$5 /Mtok) | Google's prior flagship multimodal model. Excels at code generation, mathematical reasoning, and long-context document tasks. |
| `gemini 1.5*` / `gemini-1.5*` | Gemini 1.5 Pro / Flash | ~75 / High | Mid ($0.35/$1.05 /Mtok) | Strong previous-gen Gemini. Used for document understanding, video/audio analysis, and RAG pipelines with very long context windows (up to 2M tokens). |
| `gemini 1.*` / `gemini-1*` | Gemini 1.0 Pro | ~68 / Mid | Mid | Earlier Gemini generation; largely superseded by 1.5/2.0. |
| `gemini enterprise standard subscription*` | Google Workspace AI (Standard) | N/A — SaaS seat licence | SaaS flat fee | Google Workspace AI productivity features for enterprise users. Not an inference API — no token I/O ratio applies. Exclude from model spend analysis. |
| `gemini enterprise plus subscription*` | Google Workspace AI (Plus) | N/A — SaaS seat licence | SaaS flat fee | Extended Workspace AI seat licence with advanced productivity features. Exclude from model spend analysis. |
| `gemini enterprise frontline subscription*` | Google Workspace AI (Frontline) | N/A — SaaS seat licence | SaaS flat fee | Frontline worker Workspace AI licence. Exclude from model spend analysis. |
| `amazon nova*` | Amazon Nova | ~67 / Mid | Low | AWS-native multimodal model. Suitable for low-cost document processing, image classification, and content moderation workloads within the AWS ecosystem. |

### Mapping reference — Open-Weight and Specialist Models

| AI Model value | AA Model Name (exact) | Quality Index | Price Tier | Use Case |
|---|---|---|---|---|
| `kimi k2.5` | Kimi K2.5 | ~77 / High | Low ($0.14/$1.40 /Mtok) | Moonshot AI's reasoning-focused model. Competitive with Sonnet-tier models on coding and STEM tasks at a fraction of the cost. Strong pick for batch code analysis and structured extraction. |
| `deepseek*` / `deepseek-v3*` | DeepSeek V3 | ~79 / High | Very Low ($0.07/$1.10 /Mtok) | Chinese open-weight frontier model. Exceptional price/quality ratio; AA rates it near GPT-4o on most benchmarks. Well-suited for coding, reasoning, and high-volume inference. |
| `deepseek-r1*` | DeepSeek R1 | ~80 / High | Very Low ($0.14/$2.19 /Mtok) | DeepSeek's reasoning-chain variant. Optimised for step-by-step problem solving and mathematical tasks. |
| `qwen3*` | Qwen3 | ~75 / High | Very Low ($0.02/$0.06 /Mtok) | Alibaba's latest open-weight model. Strong multilingual performance and coding capability. Extremely cost-efficient for high-volume batch inference. |
| `qwen2*` | Qwen2.5 | ~72 / High | Very Low ($0.01/$0.03 /Mtok) | Previous Qwen generation; still strong for structured tasks and multilingual workloads at near-zero cost. |
| `llama 4 maverick*` / `llama-4-maverick*` | Llama 4 Maverick | ~75 / Mid-High | Very Low (OSS) | Meta's larger Llama 4 variant. Good for complex reasoning and code tasks as a self-hosted option. Competitive with Sonnet-tier on coding benchmarks. |
| `llama 4 scout*` / `llama-4-scout*` | Llama 4 Scout | ~71 / Mid-High | Very Low (OSS) | Meta's efficient Llama 4 variant. Designed for fast inference; suitable for classification, summarisation, and lightweight agentic tasks. |
| `llama 3.3*` / `llama 3.3 70b` | Llama 3.3 70B | ~72 / Mid | Very Low (OSS) | Strong open-weight 70B model from Meta. Solid general-purpose model for summarisation, Q&A, and instruction-following. |
| `llama 3.1*` / `llama-3.1*` | Llama 3.1 | ~68 / Mid | Very Low (OSS) | Meta's widely-adopted previous-gen open model. Used extensively for self-hosted inference and fine-tuning. |
| `llama 3*` / `llama-3*` | Llama 3 | ~65 / Mid | Very Low (OSS) | Baseline Meta open-weight model. Good for simple classification and low-stakes generation tasks. |
| `llama-3.1-8b` | Llama 3.1 8B | ~58 / Mid | Very Low (OSS) | Lightweight 8B parameter model. Best for edge/latency-sensitive classification or on-device inference. Not suitable for complex reasoning. |
| `gemma 3 12b` | Gemma 3 12B | ~65 / Mid | Very Low (OSS) | Google's open-weight model optimised for efficiency. Suitable for structured extraction, content moderation, and lightweight reasoning tasks. |
| `minimax m2.5` | MiniMax M2.5 | ~65 / Mid | Low ($0.20/$1.10 /Mtok) | MoE-architecture model from MiniMax. Efficient for long-context document tasks and dialogue. Cost-effective alternative to Sonnet for lower-complexity workloads. |
| `glm-5` | GLM-5 | ~66 / Mid | Very Low ($0.05/$0.15 /Mtok) | Zhipu AI's latest model. Strong for Chinese-language tasks and structured data extraction. Very low cost per token. |
| `nvidia nemotron*` | Nemotron (NVIDIA) | ~70 / Mid | Low | NVIDIA's fine-tuned Llama-based model optimised for enterprise instruction-following and customer-service automation. |
| `cohere rerank*` | Cohere Rerank 3.5 | N/A — Reranker | Low (search API) | Purpose-built reranking model for RAG pipelines. Not a generative LLM — scores retrieved documents for relevance. No token I/O ratio applies. |
| `cohere*` | Cohere Command | ~65 / Mid | Low | Cohere's enterprise generative model. Designed for business text generation, summarisation, and grounded Q&A. |
| `mistral large*` | Mistral Large | ~76 / High | Mid ($2/$6 /Mtok) | Mistral's flagship dense model. Strong for code, reasoning, and multilingual tasks. Competitive with GPT-4o on many benchmarks at lower cost. |
| `mistral small*` / `mistral*` | Mistral Small | ~68 / Mid | Low ($0.10/$0.30 /Mtok) | Lightweight Mistral model for high-volume, low-complexity tasks. Good balance of speed and capability for structured workloads. |

### Verdict rules (apply per model)

| Condition | Verdict |
|---|---|
| Premium/High price tier AND input ratio > 85% AND quality index > 80 | ⚠ **Overpaying** — high-quality model used for low-complexity input-heavy workload |
| Premium price tier AND input ratio 70-85% | △ **Watch** — monitor whether quality differential justifies cost |
| Mid price tier OR (Premium tier AND input ratio < 70%) | ✓ **Optimal** — appropriate quality/cost balance |
| Low/Very Low price tier | ✓ **Optimal** — cost-efficient |
| Reranker / retrieval-only | ~ **Justified** — purpose-built tool |
| Spend < $50 AND not a primary model | - **Exploratory** — trial/experiment, no action needed |

---

## Step 4 — Compute I/O Ratio per Model

From the 2b token breakdown:
- `input_pct` = `input tokens cost` / (`input tokens cost` + `output tokens cost`) x 100
- `output_pct` = 100 - `input_pct`
- If a model only has `other` token type (e.g. Cohere reranker), mark as `N/A`

---

## Step 5 — Derive Savings Opportunities

For each model with verdict **Overpaying** or **Watch**, compute an opportunity card:
- **Suggested alternative**: next cheaper model family with quality index within 10 points
- **Estimated savings**: `current spend x (1 - (alt_price / current_price))`
  Use price tier midpoints: Premium=$45/Mtok blended, High=$6, Mid=$9, Low=$0.75, Very Low=$0.10
- **Signal**: describe what the I/O ratio implies about the workload type

Always include one **"Well-calibrated models"** card for Optimal-verdict models showing they are
correctly tiered — this reinforces good behaviour.

---

## Step 6 — Build the HTML Report

Use `create_html_artifact` with id `ai_model_intelligence_report`.

### Layout (in order)
1. **Header** — customer display name + "AI Model Intelligence Report" + date range. Apply branding colors.
2. **KPI strip** (4 cells): Total AI Spend, # Models Active, Top Model % share, Est. Savings Opportunity
3. **Explainer box** — one sentence each on Quality Index, Price Tier, I/O Ratio, Verdict
4. **Model table** — one row per model with non-zero spend. Each model occupies **two rows**:
   - **Row 1 (data row)** — columns: `Model (Cloudability)` | `AA Match` | `Spend` | `Spend %` | `Spend Bar` | `AA Quality Index` | `Price Tier` | `I/O Ratio` | `Verdict`
   - **Row 2 (detail row)** — a full-width cell spanning all columns, light background (`#f7f8fa`),
     containing two pieces of text:
     - **Use case** (italic, muted): the AA use-case description for this model from the mapping table
     - **Verdict commentary** (normal weight): 1-2 sentences explaining *why* this verdict was assigned,
       referencing the specific I/O ratio, price tier, and quality index for this model.
       Example: "Claude Opus 4.8 is the highest-quality model on the leaderboard, but an 89% input
       ratio strongly suggests batch classification or RAG workloads — tasks where Claude Sonnet 4.6
       delivers near-identical quality at 5x lower cost."
   - Sort all models by `unblended_cost DESC`
   - Group tail models (spend < $50) into a single summary row (no detail row needed for the group)
5. **Opportunity cards** — 2-column grid, one card per Overpaying/Watch model + one "Well-calibrated" card
6. **Footnote** — data sources, model name mapping caveat, price tier disclaimer
7. **Footer** — "Made with IBM Bob | [Customer] FinOps | Data: Cloudability and Artificial Analysis | [date]"

### Design rules
- Max-width 900px, centered, single column
- No animations, no gradients, no external assets
- Quality index pill colors: Top (blue `#dbeafe`), High (green `#dcfce7`), Mid (yellow `#fef9c3`), Low (red `#fee2e2`)
- Price tier pill colors: Premium (pink), High (red-light), Mid (orange-light), Low (green-light)
- Verdict pill colors: Overpaying (red), Watch (amber), Optimal (green), Justified (yellow), Exploratory (gray)
- I/O ratio shown as a small inline two-tone bar (input=primary brand color, output=lighter shade)
- Spend bar width proportional to max spend model = 100%
- Detail row text: use-case in `font-style:italic; color:#57606a`, verdict commentary in `color:#1a1a2e`; separate with a thin `<hr>`

---

## Step 7 — Inline Summary

After the artifact, respond in chat with:
- One-paragraph narrative of the biggest finding
- A 3-row table: Model | Spend | Verdict | Est. Savings
  (top 3 by spend only)
- One sentence on the total savings opportunity
