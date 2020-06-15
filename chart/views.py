import json
from django.shortcuts import render
from django.http import JsonResponse
from .models import Passenger
from django.db.models import Count, Q


def world_population(request):
    return render(request, 'world_population.html')


def titanic(request):
    return render(request, 'titanic.html', {'chart': survive()})


def survive():
    dataset = Passenger.objects \
        .values('ticket_class') \
        .annotate(survived_count=Count('ticket_class', filter=Q(survived=True)),
                  not_survived_count=Count('ticket_class', filter=Q(survived=False))) \
        .order_by('ticket_class')

    categories = list()
    survived_series_data = list()
    not_survived_series_data = list()
    survived_rate = list()

    for entry in dataset:
        categories.append('%s 등석' % entry['ticket_class'])
        survived_series_data.append(entry['survived_count'])
        not_survived_series_data.append(entry['not_survived_count'])
        survived_rate.append(entry['survived_count'] / (entry['survived_count'] + entry['not_survived_count']) * 100.)

    chart = {
        'chart': {
            'zoomType': 'xy',
        },
        'title': {'text': 'Titanic Survivors by Ticket Class'},
        'xAxis': {'categories': categories},
        'yAxis': [{
            'labels': {
                'format': '{value}%'
            }, 'title': {
                'text': '생존율'
            },
        }, {
            'labels': {
                'format': '{value}명'
            }, 'title': {
                'text': '인원'
            },
            'opposite': 'true'
        }, ],
        'tooltip': {
            'shared': 'true'
        },
        'legend': {
            'layout': 'horizontal',
            'align': 'left',
            'x': 10,
            "verticalAlign": 'bottom',
            "y": 20,
            'floating': 'true'
        },
        'series': [{
            'name': '생존',
            'type': 'column',
            'yAxis': 1,
            'data': survived_series_data,
            'color': '#93CC8D',
            'tooltip': {'valueSuffix': '명'}
        }, {
            'name': '비생존',
            'type': 'column',
            'yAxis': 1,
            'color': '#BB2929',
            'data': not_survived_series_data,
            'tooltip': {'valueSuffix': '명'}
        }, {
            'name': '생존율',
            'type': 'spline',
            'data': survived_rate,
            'tooltip': {'valueSuffix': '%'}
        },
        ]
    }

    dump = json.dumps(chart)
    return dump


def covid19(request):
    return render(request, 'covid.html', {'chart': corona()})


import pandas as pd
from datetime import timezone, datetime
import arrow

def datetime(o):
    if isinstance(o, datetime):
        return o.__str__()

def corona():
    df = pd.read_csv('https://raw.githubusercontent.com/datasets/covid-19/master/data/countries-aggregated.csv',
                     parse_dates=['Date'])

    countries = ['Korea, South', 'Germany', 'United Kingdom', 'US', 'France']
    df = df[df['Country'].isin(countries)]

    df['Cases'] = df[['Confirmed']].sum(axis=1)

    df = df.pivot(index='Date', columns='Country', values='Cases')

    countries = list(df.columns)

    covid = df.reset_index('Date')

    covid.set_index(['Date'], inplace=True)
    covid.columns = countries

    populations = {'Korea, South': 51269185, 'Germany': 83783942, 'United Kingdom': 67886011, 'US': 331002651,
                   'France': 65273511}
    percapita = covid.copy()
    for country in list(percapita.columns):
        percapita[country] = percapita[country] / populations[country] * 1000000

    my_data = list()

    for country in list(percapita.columns):
        my_series = list()
        for d in percapita.index.tolist():
            my_series.append([arrow.get(d.year, d.month, d.day).timestamp * 1000, round(percapita.loc[d][country], 1)])

        my_dict = dict()
        my_dict['country'] = country
        my_dict['series'] = my_series
        my_data.append(my_dict)

    print(list(map(
        lambda entry: {'name': entry['country'], 'data': entry['series']},
        my_data)))


    chart = {
        'chart': {
            'type': 'spline',
        },
        'title': {'text': 'COVID-19 확진자 발생율'},
        'subtitle': {'text': 'Source: Johns Hopkins University Center for Systems Science and Engineering'},
        'xAxis': {'type': 'datetime',

        },
        'yAxis': [{
            'labels': {
                'format': '{value} 건/백만 명',
            }, 'title': {
                'text': '합계 건수',
            },
        }, ],
        'plotOptions': {
            'spline': {
                'lineWidth': 3,
                'states': {
                    'hover': {'lineWidth': 10}
                },

            }
        },
        'series': list(map(
                    lambda entry: {'name': entry['country'], 'data': entry['series']},
                    my_data)
        ),
        'navigation': {
            'menuItemStyle': {'fontSize': '10px'}
        },
    }
    dump = json.dumps(chart, default=datetime)
    return dump


