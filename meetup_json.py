import collections
import json
import os.path
from pprint import pprint
from operator import itemgetter
import csv
import re
import time

# Aggregating event data
city = 'Baltimore'
# city = 'Pittsburgh'
i = 0
groups = {}
num_events = 0
events = {}

for month in {"09-01_", "10-01_", "10-28_", "11-08_"}:
    i = 0
    for x in range(0, 10):
        file = '/Users/myeong/git/meetup/data/json/Events_2015-' + month + city + '_' + str(i) + '.json'
        
        if os.path.isfile(file):  
            pprint("Entered: ")      
            pprint(file)
            with open(file) as data_file:    
                data = json.load(data_file)
                
                for element in data['results']:    
                    index = element['group']['id']
                    
                    # making event list               
                    venue = element['venue'] if 'venue' in element else ''
                    description = element['description'] if 'description' in element else ''
                    t = element['time'] if 'time' in element else ''
                    t = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(t/1000.0))
                    TAG_RE = re.compile('<.*?>')
                    description = re.sub(TAG_RE, '', description)
                    rsvp_limit = str(element['rsvp_limit']) if 'rsvp_limit' in element else ''
                    yes_rsvp_count = str(element['yes_rsvp_count']) if 'yes_rsvp_count' in element else ''
                    visibility = element['visibility'] if 'visibility' in element else ''
                    join_mode = element['group']['join_mode'] if 'group' in element else ''
                    fee = element['fee'] if 'fee' in element else ''
                    
                    
                    if venue != '':
                        ecity = venue['city'] if 'city' in venue else ''
                        address = venue['address_1'] if 'address_1' in venue else ''
                        vlon = venue['lon'] if 'lon' in venue else ''
                        vlat = venue['lat'] if 'lat' in venue else ''                    
                        events[element['id']] = str(index)  + ', ' + element['id'] + ', ' + element['name'].replace(',', '') + ', ' + t + ', ' + description.replace(',', '') + ', ' 
                        events[element['id']] += venue['name'].replace(',', '') + ', ' + ecity.replace(',', '') + ', ' + address.replace(',', '') + ', ' + str(vlon) + ', ' + str(vlat)
                        events[element['id']] += ',' + rsvp_limit + ',' + yes_rsvp_count + ',' + visibility + ',' + join_mode
                        if fee!='':
                            events[element['id']] += ',' + str(element['fee']['amount']) + ',' + element['fee']['description']+ ',' + element['fee']['label'] + ',' + str(element['fee']['required']) + ',' + element['fee']['accepts']  
                    else:
                        events[element['id']] = str(index) + ', ' + element['id'] + ', ' + element['name'].replace(',', '') + ', ' + t + ', ' + description.replace(',', '') + ', No venue'
                        events[element['id']] += ',"","","","",' + rsvp_limit + ',' + yes_rsvp_count + ',' + visibility + ',' + join_mode
                        if fee!='':
                            events[element['id']] += ',' + str(element['fee']['amount']) + ',' + element['fee']['description']+ ',' + element['fee']['label'] + ',' + str(element['fee']['required']) + ',' + element['fee']['accepts']
                    
                    #detecting groups that organized events 
                    if index in groups:
                        groups[index] = groups[index] + 1       
                    else:
                        groups[index] = 1
                    num_events += 1
                i += 1
    
        else:
            break

print(len(events))       
groups = list(groups.items())
groups = sorted(groups, key=itemgetter(1))
groups.reverse();
groups = collections.OrderedDict(groups)
#pprint(groups)
pprint('Number of total events:' + str(num_events))
pprint('Number of groups having events:' + str(len(groups)))

# Group-based analysis
def getGroupName(k, group_list):
    for key in group_list:
        if key == k:            
            return group_list[key]
    return ''

i=0
group_string = []
group_list = {}

for month in {"09-01_", "10-01_", "10-28_", "11-08_"}:
    i = 0
    for x in range(0, 10):
        file = '/Users/myeong/git/meetup/data/json/Group_2015-' + month + city + '_' + str(i) + '.json'
        
        if os.path.isfile(file):        
            pprint(file)
            with open(file) as data_file:    
                data = json.load(data_file)
                
                for element in data['results']:
                    organizer = element['organizer']['name'] if 'organizer' in element else ''
                    category = element['category']['shortname'] if 'category' in element else ''
                    ecity = element['city'] if 'city' in element else ''
                    lon = element['lon'] if 'lon' in element else ''
                    lat = element['lat'] if 'lat' in element else ''
                    
                    description = element['description'] if 'description' in element else ''
                    TAG_RE = re.compile('<.*?>')
                    description = re.sub(TAG_RE, '', description)
                    
                    topics = ''
                    if len(element['topics']) > 0:
                        for topic in element['topics']:
                            topics = topics + str(topic['name']) + '; ' 
                    group_list[element['id']] = element['name'].replace(',', '') + ", " + description.replace(',','') + ',' + ecity.replace(',', '') + ", "      
                    group_list[element['id']] += category.replace(',', '') + ", " + str(lon) + ", " + str(lat) 
                    group_list[element['id']] += ", "  + topics.replace(',', '')
                    
                i += 1
        else:
            break

i=0
num_outside = 0
num_event_out = 0
for key in groups:
    name = getGroupName(key, group_list)
    i+=1    
    if name == '':
        num_outside += 1
        num_event_out += groups[key]
        continue
    group_string.append(str(key) + ', ' + str(groups[key]) + ', ' + name)

pprint("Number of groups from outside of " + city + ": " + str(num_outside))
pprint("Number of events from groups outside of  " + city + ": " + str(num_event_out))
# pprint(group_string)

with open('/Users/myeong/git/meetup/data/cleaned_data_' + city + '.csv', 'w',  newline='') as csvfile: 
    i=0
    writer = csv.writer(csvfile, delimiter=' ', quotechar='|')    
    for k in group_string:                  
        i+=1
        group_id = k.split(',')
        group_id = group_id[0]
#         print(group_id)
        for key in events:
#             print(event)            
            gid = events[key].split(',')
            gid = gid[0]
            
            if group_id == gid:
                row = k + ',' + events[key]
                writer.writerow([row.encode("UTF-8")])                
        
    print ("Complete " + str(i)+ " rows!")


