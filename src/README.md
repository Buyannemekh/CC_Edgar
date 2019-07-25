This is the directory where your source code would reside.

# Insight Data Engineering Challenge - Edgar Analytics

This project was building a pipeline to ingest that stream of data and calculate how long a particular user spends on EDGAR during a visit and how many documents that user requests during the session.

## Getting Started 

I have developed the pipeline in Python. The packages that I have used: csv, datetime, time, os. 
To run: run run.sh that has python src/sessionization.py

### Reading .csv file

Added 'utf8-sig' encoding option. 
```
('log.csv', mode='r', encoding='utf-8-sig')
```

### Epoch

I have converted the date and time to epochs, so it's convenient for storage and comparing dates. Especially, this is helpful when 
inactivity_period is greater than 1 day. Epochs allow us to distinguish 2017-06-31 00:00:00 is later than 2017-06-30 00:00:01.
Converted 2017-06-30 00:00:00 to epochs, so that it's feasible to keep track of inactivity_period

```
2017-06-30 00:00:00 is equal to 1498795200 in epochs
```

### Data Structure 

The main structure consists of layers of dictionaries. 

The general big dictionary has a key which is date and time in epochs
                                          and a value is dictionary that has a key which is IP address.

```
{datetime: {IP: {first_accessed_datetime: v1, last_accessed_datetime:v2, number_of_doc:v3}}}
```


```
{1498795200: {'101.81.133.jja': {'old datetime': 1498795200, 'datetime': 1498795200, 'doc': 1}, 
                         '107.23.85.jfd': {'old datetime': 1498795200, 'datetime': 1498795200, 'doc': 2}}}
```


After adding row information from .csv to the dictionary make sure if there are any IP that has been idle for more than inactivity_period time, 
if there is print that information and remove it from the dictionary.

When it reaches the end of file, write out results to the output file in desired fashion. 
To do this, I have converted the dictionary to list first so that it'd be feasible to sort. 

```
dr =sorted(sort_this_dict.items(), key= lambda dct: (dct[1]['old datetime'], dct[1]['datetime'] ))
```
