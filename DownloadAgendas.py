import os
import json
from tqdm import tqdm
from openai import OpenAI
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

for year in range(2017, 2025):
    if year == 2024:
        months = range(1, 5)
    elif year == 2017:
        months = range(5, 13)
    else:
        months = range(1, 13)
    for month in tqdm(months):
        url = f'https://api.coastal.ca.gov/agendas/v1/{year}/{month}'
        response = requests.get(url)
        if response.status_code == 200 and response.json():
            agendas = response.json()
            #Save pretty json to file
            with open(f'./Agendas/{year}_{month}.json', 'w') as file:
                file.write(json.dumps(agendas, indent=4))

files = os.listdir('./Agendas')
files = [file for file in files if file.endswith('.json')]
files.sort()
for filename in tqdm(files):
    print(filename)
    with open('./Agendas/' + filename, 'r') as file:
        agendas = json.load(file)[0]
    items = []
    month = agendas['month']
    year = agendas['year']
    days = agendas['days']
    for day in days:
        date = day['date']
        current_options = day['districts']
        for district in current_options:
            district_name = district['name']['english']
            if 'categories' not in district:
                continue
            agenda_items = district['categories']
            for item in agenda_items:
                if 'number' not in item:
                    print(item)
                    continue
                item_number = item['number']
                item_title = item['title']['english']
                if 'blurb' in item:
                    item_blurb = item['blurb']['english']
                else:
                    item_blurb = ''
                if 'items' in item:
                    for i in item['items']:
                        subitem_number = i['letter']
                        subitem_title = i['title']['english']
                        if 'blurb' in i and i['blurb']['english']:
                            subitem_blurb = i['blurb']['english']
                        else:
                            subitem_blurb = ''
                        if 'result' in i and i['result']:
                            subitem_status = i['result']
                        else:
                            subitem_status = ''
                        items.append({
                            'date': month + ' ' + str(date) + ', ' + str(year),
                            'district': district_name,
                            'item_number': item_number,
                            'item_title': item_title,
                            'item_blurb': item_blurb,
                            'subitem_number': subitem_number,
                            'subitem_title': subitem_title,
                            'subitem_blurb': subitem_blurb,
                            'subitem_status': subitem_status
                        })
                else:
                    items.append({
                        'date': month + ' ' + str(date) + ', ' + str(year),
                        'district': district_name,
                        'item_number': item_number,
                        'item_title': item_title,
                        'item_blurb': item_blurb,
                        'subitem_number': '',
                        'subitem_title': '',
                        'subitem_blurb': '',
                        'subitem_status': ''
                    })
    with open('./AgendaItems/' + filename, 'w') as file:
        file.write(json.dumps(items, indent=4))

files = os.listdir('./AgendaItems')
files = [file for file in files if file.endswith('.json')]
files.sort()
all_agendas = []
housing_related = []
for file in files:
    with open('./AgendaItems/' + file, 'r') as f:
        agendas = json.load(f)
    all_agendas.extend(agendas)

for agenda in tqdm(all_agendas):
    agenda
    blurb = agenda['subitem_blurb']
    if blurb == '':
        continue
    messages = [
        {'role': 'user', 'content': f'Does this agenda item relate to housing? Return only "yes" or "no".\n\n{blurb}'}
    ]
    response = client.chat.completions.create(model="gpt-4-turbo", messages=messages)
    response = response.choices[0].message.content
    if response.startswith('Yes') or response.startswith('Yes'):
        housing_related.append(agenda)

with open('./HousingAgendaItems.json', 'w') as file:
    file.write(json.dumps(housing_related, indent=2))

with open('./HousingAgendaItems.json', 'r') as file:
    housing_agendas = json.load(file)

multifamily = []
for agenda in tqdm(housing_agendas):
    messages = [
        {'role': 'user', 'content': f'Does this agenda item relate to multi-unit/multi-family housing? Return only "yes" or "no".\n\n{agenda["subitem_blurb"]}'}
    ]
    response = client.chat.completions.create(model="gpt-4-turbo", messages=messages)
    response = response.choices[0].message.content
    if response.startswith('Yes') or response.startswith('Yes'):
        multifamily.append(agenda)

with open('./MultifamilyAgendaItems.json', 'w') as file:
    file.write(json.dumps(multifamily, indent=2))

with open('./MultifamilyAgendaItems.json', 'r') as file:
    multifamily_agendas = json.load(file)

unit_count = {}
for agenda in tqdm(multifamily_agendas):
    year = agenda['date'].split(', ')[1]
    if year not in unit_count:
        unit_count[year] = 0
    messages = [
        {'role': 'user', 'content': f'How many units were approved by the commission with this agenda item? Only give a number. If not approved, say 0. If no housing units were proposed, say 0.\n\n{agenda["subitem_blurb"]}\n\nStatus: {agenda["subitem_status"]}'}
    ]
    response = client.chat.completions.create(model="gpt-4-turbo", messages=messages)
    response = response.choices[0].message.content
    print(response)
    unit_count[year] += int(response)

print(unit_count)