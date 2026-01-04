# Longitudinal Study: Creative Professional Health & Well-being
## A Multi-Agent Approach to Understanding Artist/Musician Health Outcomes

---

## Executive Summary

**Study Title**: "Life-Long Creatives Health Surveillance Study: A Comprehensive Analysis of Mortality, Mental Health, and Economic Displacement Among Non-Famous Artists and Musicians"

**Purpose**: Address the critical gap in understanding health outcomes, economic displacement, and workforce resilience among working creative professionals (musicians, photographers, visual artists, etc.) through a nationwide longitudinal study.

**NIH Funding Mechanism**: R61/R33 Phased Innovation Award for Music and Health (PAR-20-266)

**Key Innovation**: First comprehensive study focusing on NON-FAMOUS creative professionals across multiple disciplines, incorporating novel data sources (streaming economics, AI displacement, gig economy metrics) with traditional health surveillance.

---

## Multi-Agent System Contributions

### 1. **Grant Writing Agent** - NIH Application Development

**Role**: Lead the R61/R33 grant application preparation

**Key Tasks**:
- ✅ **Format Compliance**: Ensure PDF formatting meets NIH standards
- ✅ **Page Limits**: Research Strategy (12 pages), Specific Aims (1 page)
- ✅ **R61/R33 Structure**: Design phased milestones
- ✅ **Go/No-Go Criteria**: Define quantifiable transition metrics
- ✅ **Budget Justification**: $350K/year direct costs maximum

**Specific Contributions**:

#### Specific Aims (1 Page)
```
AIM 1 (R61): Establish feasibility of nationwide creative professional
health surveillance system
- Sub-aim 1a: Recruit and retain 500 working artists/musicians across
  disciplines
- Sub-aim 1b: Validate novel data collection instruments (streaming
  economics, AI displacement)
- Sub-aim 1c: Link individual-level data with existing surveillance
  systems (NDI, WONDER)

AIM 2 (R33): Conduct 5-year longitudinal health outcomes study of 5,000
creative professionals
- Sub-aim 2a: Measure mortality rates by creative discipline
- Sub-aim 2b: Quantify mental health outcomes (depression, anxiety,
  suicidality)
- Sub-aim 2c: Assess economic displacement effects on health
- Sub-aim 2d: Identify protective vs. risk factors by discipline type
```

#### Go/No-Go Milestones (R61 → R33)
```
MILESTONE 1: Achieve ≥80% retention rate in pilot cohort (Month 12)
MILESTONE 2: Successfully link ≥90% of participants to NDI records (Month 18)
MILESTONE 3: Validate economic displacement instruments (α ≥ 0.80) (Month 18)
MILESTONE 4: Demonstrate feasibility of granular categorization
              (hip hop vs classical, etc.) (Month 24)
```

---

### 2. **Dataset Agent** - Data Identification & Integration

**Role**: Identify, catalog, and provide loading instructions for all relevant datasets

**Data Sources Identified**:

#### **Mortality & Health Surveillance**
```python
# CDC WONDER (Wide-ranging Online Data for Epidemiologic Research)
# - Mortality data by occupation code
# - Cause of death (ICD-10 codes)
# - Geographic distribution

# National Death Index (NDI)
# - Individual-level mortality linkage
# - Cause-specific mortality

# NHANES (National Health and Nutrition Examination Survey)
# - Cross-sectional health data
# - Audiometric testing (for tinnitus prevalence)

# BRFSS (Behavioral Risk Factor Surveillance System)
# - Mental health indicators
# - Substance use
# - State-level estimates
```

#### **Economic & Labor Data**
```python
# Current Population Survey (CPS)
# - Employment status of artists
# - Income and earnings
# - Health insurance coverage

# American Community Survey (ACS)
# - Detailed occupation codes (SOC codes for artists/musicians)
# - Income, poverty, demographics
# - Census tract-level data

# O*NET (Occupational Information Network)
# - Detailed occupation characteristics
# - Work context and activities

# Bureau of Labor Statistics (BLS)
# - Employment projections
# - Wage data by occupation
# - Occupational health statistics
```

#### **Creative Industry-Specific**
```python
# Streaming Platform Data (via APIs where available)
# - Spotify for Artists API
# - YouTube Analytics API
# - SoundCloud API
# - Artist revenue trends

# Copyright Office Data
# - Copyright registrations by type
# - Trends over time

# Arts & Culture Surveys
# - NEA Survey of Public Participation in the Arts (SPPA)
# - Americans for the Arts Creative Industries studies
```

#### **Novel Data Sources**
```python
# Gig Economy Platforms
# - Fiverr, Upwork, TaskRabbit (freelance creative work)
# - Patreon (creator economy)
# - Bandcamp (independent music sales)

# Social Media Health Surveillance
# - Twitter/X sentiment analysis (mental health signals)
# - Reddit communities (r/wearethemusicmakers, r/photography)

# COVID-19 Impact Data
# - Pandemic-specific creative worker surveys
# - Venue closure data
# - Grant/relief fund distributions
```

**Example Loading Code**:
```python
from datasets import load_dataset
import pandas as pd

# Load CDC WONDER mortality data
cdc_wonder = pd.read_csv("https://wonder.cdc.gov/controller/datarequest/D77")

# Load American Community Survey (via Census API)
import census
c = census.Census("YOUR_API_KEY")
acs_artists = c.acs5.state_county_tract(
    ('NAME', 'B24010_003E'),  # Arts, design, entertainment occupations
    census.ALL,
    census.ALL,
    census.ALL,
    year=2022
)

# Load streaming economics data (simulated)
streaming_data = load_dataset("custom/artist_streaming_revenue")
```

---

### 3. **Deep Researcher Agent** - Literature Review & Mechanism Design

**Role**: Comprehensive literature review and identification of biological/behavioral mechanisms

**Research Questions**:

#### **Mental Health Mechanisms**
- Why are musicians at higher risk for depression/suicidality?
- Does chronic financial instability mediate mental health outcomes?
- How does job insecurity in gig economy affect psychological well-being?
- Role of social support networks in creative communities

#### **Physical Health Mechanisms**
- Tinnitus and hearing loss: Dose-response by venue type and genre
- Cancer risk: Environmental exposures in performance venues
- Substance use disorders: Coping mechanisms vs. industry culture
- Sleep disorders: Impact of irregular schedules and night work

#### **Economic Displacement Mechanisms**
- Streaming revenue collapse: Income loss → health outcomes pathway
- AI displacement: Psychological impact of creative work devaluation
- Pandemic effects: Acute vs. chronic financial stress
- Copyright erosion: Long-term career viability concerns

#### **Behavioral Economics**
- Present bias and health insurance uptake among freelancers
- Mental accounting of irregular creative income
- Risk perception and protective health behaviors
- Social comparison effects in online creator economy

**Literature Synthesis**:
```
PRELIMINARY FINDINGS (from Deep Researcher Agent):

1. Existing Studies (Gaps Identified):
   - Kenny et al. (2016): Musicians' mental health - ONLY classical orchestra
   - Gross & Musgrave (2020): Sustainability in music - UK ONLY
   - Teague et al. (2022): Creative workers in pandemic - SHORT-TERM ONLY

   ❌ GAP: No US longitudinal studies on diverse creative disciplines
   ❌ GAP: No granular categorization (hip hop vs. classical)
   ❌ GAP: No integration of economic displacement metrics

2. Proposed Mechanisms:
   - Financial Precarity → Chronic Stress → HPA Axis Dysregulation →
     Depression/Anxiety
   - Social Isolation (gig economy) → Reduced Social Support →
     Suicidal Ideation
   - Hearing Damage → Tinnitus → Sleep Disruption → Depression
   - AI Displacement → Existential Threat → Hopelessness → Overdose Risk

3. Behavioral Processes:
   - Substance use as coping mechanism for performance anxiety
   - Delayed healthcare seeking due to lack of insurance
   - Network effects in creative communities (both protective and risk)
```

---

### 4. **Bloom Agent** - Evaluation Design & Behavioral Assessment

**Role**: Design evaluation framework for assessing creative workforce resilience and identifying protective factors

**Evaluation Strategy**:

#### **Behavior: Creative Workforce Resilience**
```yaml
behavior:
  name: creative-workforce-resilience
  description: "Ability of creative professionals to maintain health and
                well-being despite economic displacement and job insecurity"

understanding_phase:
  - Analyze existing resilience frameworks
  - Identify protective factors in creative communities
  - Map behavioral pathways (resilience → health outcomes)

ideation_phase:
  base_scenarios:
    - Musician facing streaming revenue loss
    - Photographer displaced by AI image generation
    - Visual artist during pandemic venue closures
  variations:
    - Genre-specific (hip hop, classical, EDM)
    - Career stage (emerging, mid-career, established)
    - Geographic (urban vs. rural, high vs. low arts funding states)

rollout_phase:
  modality: "simenv"  # Simulated economic scenarios
  target_model: "human_participants"
  max_turns: 20
  assessment:
    - Financial decision-making under uncertainty
    - Help-seeking behaviors
    - Community engagement
    - Career adaptation strategies

judgment_phase:
  primary_outcome: resilience_score (1-10)
  additional_qualities:
    - social_support_utilization
    - financial_literacy
    - mental_health_awareness
    - career_flexibility
  meta_judgment:
    - Which disciplines show highest resilience?
    - What factors predict successful adaptation?
    - How do community interventions modify outcomes?
```

#### **Behavioral Assessments**:
```
1. Economic Stress Resilience Scale (ESRS) - Novel instrument
2. Creative Identity Threat Inventory (CITI)
3. Gig Economy Work-Life Balance Measure
4. AI Displacement Anxiety Scale
5. Community Cohesion in Creative Networks
```

---

### 5. **VPN Agent** - Data Security & Privacy (if needed)

**Role**: Ensure secure data collection and transmission for sensitive health information

**Considerations**:
- HIPAA-compliant data collection
- Encrypted survey platforms
- Secure linkage to NDI/mortality records
- Participant privacy protection

---

### 6. **Project Manager Agent** - Study Coordination

**Role**: Route specific questions to appropriate specialist agents

**Routing Examples**:
```
User: "How do I format the Data Sharing Plan?"
→ Routes to: Grant Writing Agent

User: "Where can I find tinnitus prevalence data?"
→ Routes to: Dataset Agent

User: "What's the mechanism linking financial stress to suicide?"
→ Routes to: Deep Researcher Agent

User: "How do I measure workforce resilience?"
→ Routes to: Bloom Agent
```

---

### 7. **Orchestrator Agent** - Integrated Study Design

**Role**: Coordinate complex multi-agent workflows for comprehensive study planning

**Workflow Example**:
```
PHASE 1: Literature Review + Data Identification
  - Researcher Agent: Systematic review
  - Dataset Agent: Catalog data sources
  - Output: Integrated knowledge base

PHASE 2: Study Design + Grant Writing
  - Researcher Agent: Mechanism-based hypotheses
  - Bloom Agent: Behavioral assessment design
  - Grant Writing Agent: R61/R33 application
  - Output: Complete grant application

PHASE 3: Implementation Planning
  - Dataset Agent: Data acquisition procedures
  - VPN Agent: Security protocols
  - Grant Writing Agent: Budget justification
  - Output: Implementation manual
```

---

## Study Design Framework

### **R61 Phase (Years 1-2): Feasibility & Pilot**

#### **Aims**:
1. **Recruitment & Retention Feasibility**
   - Target: 500 creative professionals across 10 disciplines
   - Disciplines: Hip hop artists, classical musicians, EDM producers,
     editorial photographers, wedding photographers, visual artists,
     theater performers, dancers, filmmakers, craft artists
   - Granular categorization validated

2. **Data Collection Infrastructure**
   - Link participants to National Death Index
   - Collect baseline: health, economic, behavioral data
   - Validate novel instruments (streaming economics, AI displacement)
   - Test feasibility of record linkage (mortality, census, copyright)

3. **Preliminary Mechanism Studies**
   - Pilot cross-sectional analysis: economic stress → mental health
   - Preliminary dose-response: venue noise exposure → tinnitus
   - Feasibility of behavioral economics experiments

#### **Participant Recruitment Strategy**:
```
SOURCE 1: Online Creator Platforms
  - Spotify for Artists
  - Bandcamp
  - Patreon
  - Instagram (verified artists with <100K followers)

SOURCE 2: Professional Associations
  - American Federation of Musicians (AFM) locals
  - Professional Photographers of America (PPA)
  - Regional arts councils

SOURCE 3: Gig Economy Platforms
  - Fiverr, Upwork (creative services)
  - GigSalad, The Bash (performers)

SOURCE 4: Community-Based Recruitment
  - Music venues
  - Gallery openings
  - Photography studios
  - Recording studios
```

#### **Data Collection (Baseline)**:
```
HEALTH OUTCOMES:
  - PHQ-9 (depression)
  - GAD-7 (anxiety)
  - Columbia Suicide Severity Rating Scale (C-SSRS)
  - AUDIT (alcohol use)
  - DAST-10 (drug use)
  - Audiometric testing (tinnitus)
  - Self-reported chronic conditions

ECONOMIC MEASURES:
  - Annual income (total, creative work, non-creative work)
  - Streaming revenue (if applicable)
  - Gig economy earnings
  - Health insurance status
  - Housing stability
  - Food security (USDA module)
  - Pandemic financial impact

CREATIVE WORK CHARACTERISTICS:
  - Primary discipline (granular)
  - Years in field
  - Performance venues/exposure
  - Average hours/week creating
  - AI tool use/displacement concerns
  - Copyright registrations
  - Social media presence/following

BEHAVIORAL ECONOMICS:
  - Financial literacy
  - Risk tolerance
  - Present bias (delay discounting)
  - Health insurance decision-making
  - Social comparison (creator economy)

SOCIAL/COMMUNITY:
  - Social support networks
  - Creative community engagement
  - Union/association membership
  - Mentorship relationships
```

#### **Go/No-Go Decision Points**:
```
MONTH 12:
  ✓ Recruited ≥400 participants (80% of target)
  ✓ Retention ≥80% at 6-month follow-up
  ✓ <10% missing data on primary health outcomes

MONTH 18:
  ✓ Successful NDI linkage ≥90%
  ✓ Novel instruments validated (α ≥ 0.80, test-retest ≥ 0.75)
  ✓ Preliminary analyses show expected associations
    (p < 0.05 for financial stress → mental health)

MONTH 24:
  ✓ Retention ≥75% at 18-month follow-up
  ✓ Granular categorization demonstrated (≥30 per discipline subtype)
  ✓ Qualitative interviews completed (n=50, thematic saturation)
  ✓ Data sharing plan implemented
```

---

### **R33 Phase (Years 3-5): Full Longitudinal Study**

#### **Aims**:
1. **Mortality Surveillance (Primary Outcome)**
   - All-cause mortality rates by discipline
   - Cause-specific: suicide, overdose, cancer, cardiovascular
   - Standardized Mortality Ratios (SMR) vs. general population
   - Granular comparisons: hip hop vs. classical vs. EDM, etc.

2. **Mental Health Trajectories**
   - Longitudinal depression/anxiety/suicidality
   - Identify risk and protective factors
   - Economic displacement as time-varying predictor
   - Pandemic effects (before/during/after)

3. **Economic Displacement Effects**
   - Streaming revenue changes → health outcomes
   - AI displacement → psychological distress
   - Job loss → substance use
   - Financial shocks → healthcare access

4. **Granular Discipline Comparisons**
   - Genre-specific risks (hip hop, classical, EDM, folk, etc.)
   - Photography specialization (editorial, wedding, commercial, fine art)
   - Visual arts (painting, sculpture, digital, craft)
   - Identify high-risk subgroups

#### **Expanded Cohort**:
- **Target N**: 5,000 participants
- **Annual follow-up**: Years 3, 4, 5
- **Mortality surveillance**: Continuous (NDI linkage)

#### **Novel Data Integration**:
```
YEAR 3: Integrate real-time streaming data
  - Monthly revenue tracking (consented participants)
  - Platform-specific analytics
  - AI-generated content competition metrics

YEAR 4: Copyright & creative output
  - Link to Copyright Office registrations
  - Track career trajectory
  - Assess productivity → health associations

YEAR 5: Social media sentiment analysis
  - Longitudinal mental health signals
  - Community-level distress indicators
  - Early warning system development
```

#### **Statistical Analysis Plan**:

**Primary Analyses**:
```r
# Mortality Analysis
# Standardized Mortality Ratio
SMR <- (observed_deaths / expected_deaths) * 100

# Cox Proportional Hazards
coxph(Surv(time, death) ~ discipline + income_change +
      AI_displacement + age + sex + race + insurance_status)

# Competing Risks Regression
# Cause-specific: suicide, overdose, cancer, CVD
cmprsk::crr(time, event_type ~ discipline + covariates)
```

**Secondary Analyses**:
```r
# Longitudinal Mental Health (Mixed Models)
lme4::lmer(depression_score ~ time * economic_displacement +
           discipline + (1 | participant_id))

# Mediation Analysis
# Economic displacement → mental health → mortality
lavaan::sem(model = "
  depression ~ a*economic_displacement
  suicide_risk ~ b*depression + c*economic_displacement
  indirect := a*b
  total := c + (a*b)
")

# Machine Learning for Risk Prediction
# Random forest for high-risk identification
randomForest::randomForest(suicide_risk ~ ., data = baseline_data)
```

**Granular Comparisons**:
```r
# Within-discipline heterogeneity
# Example: Musicians only
musicians_data %>%
  filter(discipline == "music") %>%
  group_by(genre) %>%
  summarise(
    mortality_rate = sum(death) / person_years,
    mean_depression = mean(PHQ9_score),
    median_income = median(annual_income),
    AI_displacement_pct = mean(AI_displaced)
  )

# Hip hop vs. Classical vs. EDM
pairwise.t.test(depression_score, genre, p.adjust = "holm")

# Editorial vs. Wedding Photography
t.test(burnout_score ~ photo_type, data = photographers)
```

---

## Innovative Features

### 1. **Granular Discipline Taxonomy**
```
MUSIC:
├── Hip Hop
│   ├── Rap
│   ├── Production
│   └── DJing
├── Classical
│   ├── Orchestral
│   ├── Chamber
│   └── Solo
├── Electronic/EDM
│   ├── House
│   ├── Techno
│   └── Experimental
├── Jazz
├── Country
├── Folk
└── Rock/Indie

PHOTOGRAPHY:
├── Editorial
├── Wedding/Events
├── Commercial
├── Fine Art
├── Photojournalism
└── Stock

VISUAL ARTS:
├── Painting
├── Sculpture
├── Digital Art
├── Printmaking
├── Craft Arts
└── Installation

[... continued for all creative disciplines]
```

### 2. **Economic Displacement Index (EDI)**
```
Novel composite measure:
- Streaming revenue % change
- AI tool displacement (0-100 scale)
- Pandemic income loss
- Gig economy volatility
- Copyright value erosion

EDI Score = weighted sum of standardized components
```

### 3. **Real-time Surveillance Dashboard**
```
Public-facing dashboard (de-identified):
- Mortality rates by discipline (updated quarterly)
- Mental health trends
- Economic indicators
- Geographic "creative health deserts"
- Policy-relevant metrics
```

### 4. **Community-Engaged Research**
```
Artist Advisory Board:
- Co-design research questions
- Interpret findings
- Dissemination strategy
- Intervention development

Participatory Components:
- Photovoice documentation
- Creative output as data
- Community forums
- Policy advocacy training
```

---

## Data Management & Sharing

### **NIH Data Sharing Plan** (from Grant Writing Agent):

#### **Data Types**:
- De-identified survey data (health, economic, behavioral)
- Linked mortality records (restricted access)
- Streaming platform analytics (aggregated)
- Geographic identifiers (limited to state)

#### **Data Repository**:
- **ICPSR** (Inter-university Consortium for Political and Social Research)
- **NIMH Data Archive (NDA)** (for mental health components)
- **Data.gov** (public use files)

#### **Timeline**:
- Annual public use files (survey data only)
- Full dataset release 2 years post-study completion
- Restricted-use files for mortality data (application required)

#### **Access**:
- Open access: De-identified survey data
- Controlled access: Data with mortality linkage
- Tiered access: Raw streaming/economic data

---

## Budget Justification ($350K/year × 5 years)

### **R61 Phase (Years 1-2): $700K total**
```
PERSONNEL:
  PI (15% effort): $30K/year
  Co-I Epidemiologist (10%): $20K/year
  Co-I Music Therapist/Industry Expert (10%): $20K/year
  Project Coordinator (100%): $65K/year
  Data Manager (50%): $40K/year
  Research Assistants (2 × 50%): $50K/year

PARTICIPANT COSTS:
  Recruitment (n=500): $50K
  Incentives ($50/survey × 500 × 3 waves): $75K
  Audiometric testing (500 × $100): $50K

DATA/SUPPLIES:
  NDI linkage fees: $10K
  Survey platform (Qualtrics): $5K
  Data storage/security: $10K

TRAVEL:
  NIH annual meeting: $5K
  Conference presentation: $3K

TOTAL R61: $350K/year
```

### **R33 Phase (Years 3-5): $1.05M total**
```
PERSONNEL (scaled up):
  PI (20% effort): $40K/year
  Co-Is (3 × 10%): $60K/year
  Project Coordinator (100%): $70K/year
  Data Manager (100%): $85K/year
  Research Assistants (3 × 50%): $75K/year
  Statistician (25%): $30K/year

PARTICIPANT COSTS:
  Recruitment (n=5000): $100K/year (rolling)
  Incentives ($50 × 5000): $250K/year
  Mortality surveillance: $15K/year

DATA/TECHNOLOGY:
  Streaming API access: $20K/year
  Data linkage (Copyright Office, etc.): $15K/year
  Cloud storage/computing: $25K/year
  Dashboard development: $30K (Year 3 only)

DISSEMINATION:
  Annual NIH meeting: $5K/year
  Major conferences (2): $8K/year
  Community forums: $10K/year

TOTAL R33: $350K/year
```

---

## Timeline

```
YEAR 1 (R61):
  Q1: IRB approval, instrument finalization, hire staff
  Q2-Q3: Pilot recruitment (n=500), baseline data collection
  Q4: 6-month follow-up, preliminary analyses

YEAR 2 (R61):
  Q1: 12-month follow-up, Go/No-Go milestone 1
  Q2: Instrument validation, NDI linkage
  Q3: 18-month follow-up, Go/No-Go milestone 2
  Q4: Final R61 analyses, prepare for R33 transition

YEAR 3 (R33):
  Q1: R33 launch, expand recruitment to n=5000
  Q2-Q4: Baseline data collection (cohort expansion)

YEAR 4 (R33):
  Q1-Q4: Annual follow-up, mortality surveillance, real-time data integration

YEAR 5 (R33):
  Q1-Q3: Final follow-up, comprehensive analyses
  Q4: Dissemination, dashboard launch, policy briefs
```

---

## Expected Impact

### **Scientific Impact**:
- **First comprehensive US study** on non-famous creative professional health
- **Novel datasets**: Streaming economics, AI displacement, gig economy health
- **Granular insights**: Genre/discipline-specific risk profiles
- **Mechanism elucidation**: Economic precarity → health pathways

### **Public Health Impact**:
- **Surveillance system**: Real-time tracking of creative workforce health
- **Risk identification**: High-risk subgroups for targeted intervention
- **Policy evidence**: Support for artist safety nets, healthcare access
- **Intervention targets**: Modifiable risk factors identified

### **Policy Implications**:
- **Healthcare access**: Evidence for artist-specific insurance programs
- **Economic policy**: Streaming platform regulation, AI displacement mitigation
- **Occupational health**: Standards for venue noise exposure, injury prevention
- **Mental health services**: Tailored programs for creative professionals

### **Community Impact**:
- **Validation**: "Depression/suicide epidemic" documented empirically
- **Destigmatization**: Mental health issues normalized in creative communities
- **Advocacy**: Data-driven policy change efforts
- **Support**: Evidence-based peer support programs

---

## Risk Mitigation

### **Recruitment Challenges**:
- **Risk**: Low participation from underrepresented disciplines
- **Mitigation**: Community-engaged recruitment, trusted messengers,
  culturally tailored outreach

### **Retention Issues**:
- **Risk**: High attrition in gig economy workers
- **Mitigation**: Flexible follow-up schedules, multiple contact methods,
  valued incentives, community buy-in

### **Data Linkage Barriers**:
- **Risk**: NDI matching failures, missing identifiers
- **Mitigation**: Collect multiple identifiers (SSN, DOB, name variants),
  probabilistic matching algorithms

### **Sensitive Data Concerns**:
- **Risk**: Participants reluctant to share income/substance use
- **Mitigation**: Strong confidentiality protections, Certificate of
  Confidentiality, community trust-building

---

## Next Steps

### **Immediate Actions** (via Multi-Agent System):

1. **Grant Writing Agent**: Draft full R61/R33 application
   - Specific Aims (1 page)
   - Research Strategy (12 pages)
   - Go/No-Go milestones
   - Budget justification

2. **Dataset Agent**: Create comprehensive data acquisition plan
   - NDI application process
   - Census data use agreements
   - Copyright Office data access
   - Streaming platform API negotiations

3. **Researcher Agent**: Complete systematic literature review
   - Artist health outcomes (PubMed, PsycINFO)
   - Economic displacement effects (EconLit, JSTOR)
   - Behavioral economics of creative workers
   - Gap analysis for innovation justification

4. **Bloom Agent**: Develop behavioral assessment battery
   - Economic stress resilience scale
   - AI displacement anxiety measure
   - Creative identity threat inventory
   - Pilot testing protocol

5. **Project Manager**: Coordinate timeline and milestones
   - Assign tasks to agents
   - Track progress on application components
   - Integrate outputs into unified document

6. **Orchestrator**: Synthesize multi-agent contributions
   - Ensure coherence across sections
   - Resolve conflicts in approach
   - Finalize integrated application

---

## Questions for User

To refine this study design, please clarify:

1. **Primary Discipline Focus**: Do you want equal representation across all
   creative disciplines, or prioritize musicians given the NIH Music & Health FOA?

2. **Geographic Scope**: US nationwide, or focus on specific regions/states?

3. **Age Range**: All career stages, or focus on emerging artists (higher risk)?

4. **Comparison Groups**: Include non-creative workers for context?

5. **Intervention Development**: Is R61/R33 meant to inform future interventions,
   or purely observational?

6. **Community Partners**: Any existing relationships with artist organizations,
   unions, platforms?

7. **Institutional Support**: University affiliation, IRB, data infrastructure?

---

## Agent Contact Information

**To proceed with grant application development, engage agents as follows**:

```bash
# Grant Writing Agent
"Draft NIH R61/R33 Specific Aims for artist health study"
"What are page limits for Research Strategy?"
"Create budget justification for longitudinal study"

# Dataset Agent
"Find mortality data by occupation code for musicians"
"Load American Community Survey data for artists"
"Access Spotify streaming economics data"

# Researcher Agent
"Literature review on musician suicide rates"
"What mechanisms link financial stress to depression?"
"Systematic review of AI displacement effects on workers"

# Bloom Agent
"Design evaluation for creative workforce resilience"
"Create behavioral assessment for gig economy stress"
"Develop intervention to support displaced artists"

# Project Manager
"Route my question about sample size to appropriate agent"
"Coordinate grant application development across agents"

# Orchestrator
"Synthesize study design from all agent contributions"
"Create integrated timeline for R61/R33 phases"
```

---

**This is a critically important study that could transform how we understand
and support the health of creative professionals. The multi-agent system is
ready to help you develop a rigorous, compelling NIH application.**

**Let's get started!** Which component would you like to tackle first?
