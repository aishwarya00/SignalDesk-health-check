# SignalDesk Prompt Health Check
A lightweight Streamlit decision tool for evaluating AI workflow health after a prompt change.

# Track Chosen: Track A, Fictional Domain Packet.

## What I Built
A lightweight Streamlit decision support tool that compares workflow health before and after the August 4 prompt change. A teammate selects a workflow and source and receives a status of Promising, Investigate, or Inconclusive, with the observed metric movement, caveats, and a recommended next action.

#Who It Is For
Product teammates deciding what to investigate before expanding AI assisted workflows.

#Data Or Source Used
The fictional product_usage_events.csv supplied for the challenge. It contains 41 daily workflow summaries from August 1 through August 7, 2026.

#Assumptions I Made
August 4 is the comparison boundary because the dataset notes identify it as the prompt version start date. Completion and acceptance rates are calculated from summed counts. The analysis is observational and does not establish that the prompt change caused any movement.

#Data Issues Or Caveats I Noticed
I normalized inconsistent team casing, excluded a duplicate export record and demo account traffic from core metrics, and treated a review policy change as a limitation for review flag interpretation. One rating and one confidence value are missing. User rating is useful but incomplete, while model confidence is excluded from decisions because it is not a quality measure.

#What I Would Do Next With More Time
I would collect a longer comparison window, capture rating response counts, review samples of accepted and flagged outputs, and use an experiment or matched comparison group to estimate prompt impact more reliably.

