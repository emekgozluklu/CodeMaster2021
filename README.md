# CodeMaster 2021 - Solution


Go [7a324699](https://github.com/emekgozluklu/CodeMaster2021/tree/7a324699ac06a1e5dc116d371460de2e49d4b09c) to see the submitted version. Current version includes
fixes I implemented after the competition.


CodeMaster is a programming contest organized by OBSS.
In the first round, an algorithmic programming question is
asked and the top 5 people from each university is invited for
the final round. This repository contains my solution for the
final round where people from different universities compete.

In this round, we are asked to develop and API over Jira API.
We retrieve the information from Jira and convert it into desired
format. We had 4 hours to answer the question. 

Tests: 
- Submitted: `146 passed cases, 28 failed cases`
- Current: `168 passed cases, 6 failed cases`

To run the code:
- `python3 -m venv venv`
- `source venv/bin/activate`
- `export FLASK_APP=jira`
- `export FLASK_ENV=development`
- `flask run --port=8080`
