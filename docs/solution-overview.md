# Solution Overview

## Concept
**Drishti** is an explainable AI-powered crime intelligence assistant designed specifically for district-level police stations. It acts as an operational decision-support tool for the Station House Officer (SHO), transforming historical crime logs into proactive, forward-looking patrol plans.

## The Core Mechanism
Drishti works by processing raw, anonymized crime data through a multi-factor risk scoring engine rather than relying on opaque deep learning models. 

The core mechanism analyzes three main vectors:
1. **Historical Baseline**: The long-term volume of incidents in a specific micro-zone.
2. **Recency-Weighted Density**: Recent incidents (e.g., last 14 days) are exponentially weighted higher than incidents from 5 months ago, acknowledging that crime risk often clusters temporally (the near-repeat phenomenon).
3. **Trend Velocity**: Comparing the recent period against the prior period to detect emerging spikes before they become long-term problems.

## Key Design Decisions & Rationale

### 1. Explainability over Black-Box Accuracy
**Decision**: We chose a deterministic, waterfall-style heuristic model over a deep neural network for the MVP.
**Why**: Police officers must be able to trust and justify their deployments. Drishti provides a plain-language explanation for *every* prediction (e.g., "This zone is flagged because incidents have risen 23% in the last 30 days, predominantly between 8 PM and 11 PM"). A highly accurate black box that simply says "Zone 4: 87% Risk" will not be adopted by law enforcement.

### 2. The "What-If" Event Simulator
**Decision**: Building a feature that allows SHOs to artificially inject an upcoming event (like a Festival or Political Rally) into a specific zone to see how it shifts risk.
**Why**: Policing isn't just about historical data; it's about anticipating the future. By calculating historical impact multipliers for different event types, Drishti allows officers to proactively plan deployments for scheduled events rather than reacting after crimes occur.

### 3. Actionable Output (The SHO Brief)
**Decision**: Generating a downloadable, one-page PDF report rather than just a web dashboard.
**Why**: The end-user (an SHO) often needs to brief beat officers during roll call or submit deployment plans to superiors. A clean, printable PDF containing the top 5 zones, evidence, and exact patrol window suggestions bridges the gap between digital analytics and physical police work.

## The User Experience
1. **Ingest**: The user uploads standard crime data CSVs (or uses the built-in synthetic dataset).
2. **Analyze**: Drishti instantly renders a visual heatmap of all micro-zones.
3. **Investigate**: The SHO reviews the "Top 5 At-Risk Zones" table, clicking into specific zones to read the plain-language evidence.
4. **Simulate**: The SHO tests a scenario: *"We have a market day coming up in Area-12. How does that change the risk?"*
5. **Deploy**: The SHO reviews Drishti's specific patrol window recommendations (e.g., "Deploy units Fri/Sat between 20:00-23:00").
6. **Export**: The SHO clicks one button to generate the PDF Intelligence Brief for the daily roll call.
