# Grants, Fellowships, CFP & Opportunities Tracking System

**Multi-Agent Grant Management System**
**Version 1.0**
**Last Updated**: January 4, 2026

---

## 📁 System Overview

This directory contains a comprehensive tracking system for all funding opportunities including grants, fellowships, prizes, and calls for proposals (CFPs). The system is designed to be maintained by our multi-agent team, with primary responsibility assigned to the **Grant Writing Genius Agent**.

---

## 🗂️ Directory Structure

```
grants-fellowships-CFP-opportunities/
├── README.md                           # This file
├── OPPORTUNITIES_TRACKER.csv           # Master tracking spreadsheet
├── opportunities/                      # Individual opportunity files
│   └── OPPORTUNITY_001_NIDA_SUD_Startup_Challenge_2025.md
├── calendar/                          # Deadline calendars
│   └── MASTER_DEADLINE_CALENDAR.md
└── templates/                         # Templates for new opportunities
    ├── TEMPLATE_Prize_Competition.md
    ├── TEMPLATE_Research_Grant.md
    ├── TEMPLATE_Fellowship.md
    └── TEMPLATE_CFP.md
```

---

## 🎯 Purpose

### Primary Goals
1. **Centralized Tracking**: Single source of truth for all funding opportunities
2. **Deadline Management**: Never miss a submission deadline
3. **Strategic Alignment**: Prioritize opportunities that align with research
4. **Team Coordination**: Facilitate multi-agent collaboration on applications
5. **Knowledge Repository**: Document application strategies and outcomes

### Target Audiences
- Principal Investigators
- Research teams
- Grant writers
- Administrative staff
- Multi-agent system

---

## 📊 Current Opportunities

### Active (Submission Open)
1. **NIDA "$100,000 Start an SUD Startup" Challenge 2025**
   - Deadline: February 4, 2026, 6:00 PM ET
   - Amount: $10,000 per team (12 teams)
   - Priority: HIGH ⭐⭐⭐⭐⭐
   - File: `OPPORTUNITY_001_NIDA_SUD_Startup_Challenge_2025.md`

### Coming Soon (Not Yet Open)
*To be added as discovered*

### Submitted
*None yet*

### Awarded
*None yet*

---

## 🗓️ Next 90-Day Deadlines

**Current Date**: January 4, 2026

No deadlines in next 90 days. Next major deadline:
- **February 4, 2026**: NIDA SUD Startup Challenge (7 months away)

---

## 📝 How to Use This System

### Adding a New Opportunity

#### Step 1: Choose Template
Select appropriate template from `templates/`:
- **Prize Competition**: For challenge.gov prizes, innovation awards
- **Research Grant**: For R01, R21, R61/R33, and similar mechanisms
- **Fellowship**: For individual training awards (F31, F32, K awards)
- **CFP**: For conference presentations, RFPs, etc.

#### Step 2: Create Opportunity File
```bash
# Copy template
cp templates/TEMPLATE_Prize_Competition.md opportunities/OPPORTUNITY_XXX_Name_Year.md

# Fill in all sections
# Use naming convention: OPPORTUNITY_[NUMBER]_[AGENCY]_[SHORT_NAME]_[YEAR].md
```

#### Step 3: Update Tracking Systems
1. Add row to `OPPORTUNITIES_TRACKER.csv`
2. Add deadline to `calendar/MASTER_DEADLINE_CALENDAR.md`
3. Update this README if high priority

#### Step 4: Assign Agent
Tag appropriate agent for follow-up:
- Grant Writing Agent (most applications)
- Dataset Agent (data-heavy proposals)
- Researcher Agent (scientific content)
- Project Manager (coordination)

---

### Managing Deadlines

#### Calendar System
The `MASTER_DEADLINE_CALENDAR.md` includes:
- Monthly view of all deadlines
- 90-day rolling window
- Reminder schedules (90/60/30/7/1 days before)
- Action item checklists

#### Reminder Protocol
- **90 days**: Add to active tracking, begin preliminary research
- **60 days**: Assign lead writer, create timeline
- **30 days**: Draft application, internal review
- **7 days**: Final polish, format check
- **1 day**: Final review, submit early

---

### Working with Agents

#### Grant Writing Genius Agent
**Primary responsibilities**:
- Draft grant applications
- Format compliance checking
- Budget justification
- Deadline management

**Example prompts**:
```
"Review NIDA SUD Startup opportunity for alignment with artist study"
"Draft specific aims for [opportunity name]"
"Check formatting requirements for [FOA number]"
"Create submission timeline for [deadline]"
```

#### Dataset Agent
**Use when**:
- Data sources need identification
- Dataset loading instructions required
- Data sharing plans needed

**Example prompts**:
```
"Find mortality datasets for [grant application]"
"Create data sharing plan for [NIH grant]"
```

#### Deep Researcher Agent
**Use when**:
- Literature reviews needed
- Mechanism elucidation required
- Gap analysis for innovation section

**Example prompts**:
```
"Literature review for significance section on [topic]"
"What mechanisms link [exposure] to [outcome]?"
```

#### Project Manager Agent
**Use for**:
- Task routing across agents
- Timeline coordination
- Team assignments

**Example prompts**:
```
"Route my grant application tasks to appropriate agents"
"Create integrated timeline for [opportunity]"
```

#### Orchestrator Agent
**Use for**:
- Complex multi-agent workflows
- Synthesis across multiple applications
- Strategic planning

**Example prompts**:
```
"Coordinate grant application development across all agents"
"Synthesize opportunities aligned with our research"
```

---

## 📈 Priority System

### HIGH Priority ⭐⭐⭐⭐⭐
Criteria:
- Perfect alignment with research goals
- Significant funding amount
- Strong track record of success
- Opens major opportunities (e.g., SBIR/STTR pipeline)

Current HIGH priorities:
1. NIDA SUD Startup Challenge (strategic entry point to SBIR/STTR)

### MEDIUM Priority ⭐⭐⭐
Criteria:
- Good alignment with research
- Moderate funding
- Worth pursuing if capacity available

Current MEDIUM priorities:
*None yet*

### LOW Priority ⭐
Criteria:
- Tangential to research goals
- Small funding amount
- Monitor but not actively pursue

Current LOW priorities:
*None yet*

---

## 🔍 Opportunity Discovery

### Active Monitoring Sources
1. **Federal Portals**
   - Challenge.gov (prize competitions)
   - Grants.gov (federal grants)
   - NIH Guide for Grants and Contracts
   - NSF Funding Opportunities

2. **Agency-Specific**
   - NIDA funding announcements
   - NIMH funding opportunities
   - NCI grant programs
   - NCCIH initiatives

3. **Foundation Sources**
   - Foundation Center
   - Pivot database
   - Professional associations

4. **Automated Alerts**
   - Grant Forward alerts
   - NIH Guide email subscriptions
   - Challenge.gov RSS feeds
   - Institutional research office newsletters

### Discovery Workflow
1. **Weekly**: Check Challenge.gov, Grants.gov
2. **Bi-weekly**: Review NIH Guide
3. **Monthly**: Foundation Center search
4. **Quarterly**: Comprehensive landscape scan

---

## 📊 Tracking Metrics

### Success Metrics
- **Submission rate**: # submitted / # identified
- **Award rate**: # awarded / # submitted
- **Funding secured**: Total $ awarded
- **ROI**: $ awarded / effort invested

### Current Statistics
- **Total opportunities tracked**: 1
- **Applications submitted**: 0
- **Awards received**: 0
- **Total funding secured**: $0
- **Win rate**: N/A (too early)

---

## ✅ Standard Operating Procedures

### Monthly Review Process
1. **Review calendar**: Check upcoming 90-day deadlines
2. **Update statuses**: Mark submitted, awarded, closed
3. **Scan for new opportunities**: Check all sources
4. **Prioritize**: Assign priority levels
5. **Assign tasks**: Route to appropriate agents
6. **Update tracking**: CSV and calendar files

### Pre-Submission Checklist
- [ ] Read full FOA/announcement
- [ ] Contact program officer
- [ ] Assess alignment with research
- [ ] Check eligibility requirements
- [ ] Estimate budget and effort
- [ ] Assemble team
- [ ] Create submission timeline
- [ ] Draft application
- [ ] Internal review
- [ ] Format compliance check
- [ ] Submit early (buffer for technical issues)
- [ ] Confirm receipt

### Post-Submission Workflow
- [ ] Save confirmation email
- [ ] Update status in tracker
- [ ] File submission materials
- [ ] Set review date reminder
- [ ] Monitor for review outcome
- [ ] If awarded: celebrate + plan project
- [ ] If not awarded: request feedback + revise

---

## 🎯 Strategic Focus Areas

### Primary Research Themes
Based on our artist wellbeing longitudinal study:

1. **Substance Use Disorders (SUD)**
   - Overdose prevention in creative professionals
   - Addiction mechanisms in high-stress occupations
   - Economic displacement → SUD pathways

2. **Mental Health**
   - Depression and anxiety in artists
   - Suicide prevention
   - Psychological impact of economic precarity

3. **Occupational Health**
   - Tinnitus and hearing loss in musicians
   - Work-related health risks in creative professions
   - Gig economy worker health outcomes

4. **Health Disparities**
   - Healthcare access for freelance creatives
   - Underserved populations
   - Safety net policy research

5. **Behavioral Economics**
   - Financial stress and health
   - Irregular income and healthcare decisions
   - Economic shocks and coping behaviors

### Preferred Funding Mechanisms
- **SBIR/STTR**: Commercialization of research findings
- **R61/R33**: Phased innovation awards
- **R01**: Large-scale research projects
- **R21**: Exploratory/developmental research
- **Prize Competitions**: Seed funding for startups

---

## 🔧 Maintenance

### Update Schedule
- **Daily**: Check for new high-priority opportunities
- **Weekly**: Update deadline calendar
- **Monthly**: Comprehensive review and cleanup
- **Quarterly**: Strategic reassessment

### File Naming Conventions
```
Opportunities: OPPORTUNITY_[NUMBER]_[AGENCY]_[NAME]_[YEAR].md
  Example: OPPORTUNITY_001_NIDA_SUD_Startup_Challenge_2025.md

Grants: GRANT_[NUMBER]_[AGENCY]_[MECHANISM]_[YEAR].md
  Example: GRANT_002_NIH_R01_2026.md

Fellowships: FELLOWSHIP_[NUMBER]_[AGENCY]_[MECHANISM]_[YEAR].md
  Example: FELLOWSHIP_003_NIH_F32_2026.md
```

### Version Control
All files tracked in Git:
```bash
# Add new opportunity
git add grants-fellowships-CFP-opportunities/
git commit -m "feat: Add [opportunity name]"
git push
```

---

## 📞 Support & Questions

### Primary Contact
**Grant Writing Genius Agent**
- Responsible for: Application development, formatting, deadlines
- Invoke via: Natural language prompts to multi-agent system

### Backup Contacts
- **Project Manager Agent**: Task coordination
- **Orchestrator Agent**: Strategic planning
- **Research Team**: Scientific content

---

## 🚀 Quick Start Guide

### For New Team Members
1. Read this README
2. Review `MASTER_DEADLINE_CALENDAR.md`
3. Scan opportunity files in `opportunities/`
4. Familiarize with templates in `templates/`
5. Practice using agent prompts

### To Add Your First Opportunity
1. Copy relevant template
2. Fill in all sections
3. Add to CSV tracker
4. Update calendar
5. Assign to agent
6. Set reminders

### To Submit Your First Application
1. Review opportunity file
2. Engage Grant Writing Agent
3. Follow pre-submission checklist
4. Use reminder protocol
5. Submit early
6. Update status

---

## 📚 Additional Resources

### NIH Grant Resources
- [NIH Grants Policy Statement](https://grants.nih.gov/grants/policy/nihgps/index.htm)
- [SF424 Application Guide](https://grants.nih.gov/grants/how-to-apply-application-guide.html)
- [NIH SBIR/STTR](https://sbir.nih.gov/)

### Writing Resources
- [NIH Grant Writing Tips](https://grants.nih.gov/grants/grant_tips.htm)
- [Sample Applications](https://www.niaid.nih.gov/grants-contracts/sample-applications)
- [Review Criteria](https://grants.nih.gov/grants/peer-review.htm)

### Tools
- [NIH RePORTER](https://reporter.nih.gov/) - Search funded grants
- [NIH Budget Tool](https://grants.nih.gov/grants/budgeting-tools.htm)
- [eRA Commons](https://commons.era.nih.gov/)

---

## 📝 Change Log

### Version 1.0 (January 4, 2026)
- Initial system creation
- Added NIDA SUD Startup Challenge 2025
- Created all templates
- Established tracking infrastructure
- Integrated multi-agent system

---

**Maintained by**: Multi-Agent Grant Tracking System
**Primary Agent**: Grant Writing Genius Agent
**Last Review**: January 4, 2026
**Next Review**: February 1, 2026
