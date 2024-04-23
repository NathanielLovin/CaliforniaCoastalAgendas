# California Coastal Commission Agenda Processing

Inspired by [Louis Mirante](https://twitter.com/louismirante/status/1782544131245625668) and [Dave Guarino](https://twitter.com/allafarce/status/1782805511383167063), attempting to analyze the California Coastal Commission's agenda items for number of multifamily homes approved.

Data range goes from May of 2017 to April of 2024, because of the availability of the API to that period. (Older agendas, going back to 1995, are available, but in a different format that would be easy to process but additional effort at this point.)

Process: Download the agendas from the API, extract the agenda items, ask GPT-4-Turbo if the item is about housing, store the ones that are in HousingAgendaItems.json, then ask GPT-4-Turbo if each of the housing items is about multifamily housing, store the ones that are in MultifamilyHousingAgendaItems.json. I also asked GPT-4-Turbo how many units were approved for each of the multifamily housing items, but the results were not reliable. However, I will provide them below for reference.

Year | Units Approved
--- | ---
2017 | 162
2018 | 19
2019 | 453
2020 | 476
2021 | 240
2022 | 51
2023 | 333
2024 | 380