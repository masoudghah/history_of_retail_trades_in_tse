from django.shortcuts import render
from django.views import View
from persiantools.jdatetime import JalaliDate

from .models import Instrument

import datetime
import finpy_tse as fpt
import json


class RetailHistoryTrades(View):
    def get(self, request):
        instruments = Instrument.objects.all()
        thirty_days_ago = JalaliDate(datetime.datetime.now() - datetime.timedelta(days=30)).strftime("%Y-%m-%d")
        today = JalaliDate(datetime.datetime.now()).strftime("%Y-%m-%d")
        
        context = {
            'instruments': instruments,
            'symbol_input': 'پالایش',
            'start_date_input': thirty_days_ago,
            'end_date_input': today,
        }
        return render(request, 'retail_trades_history.html', context)

    def post(self, request):
        instruments = Instrument.objects.all()
        params = request.POST.dict()
        input_symbol = params['symbol_input']
        input_start_date = params['start_date_input']
        input_end_date = params['end_date_input']

        left = fpt.Get_RI_History(
            stock=input_symbol, start_date=input_start_date, end_date=input_end_date,
            ignore_date=False, show_weekday=True, double_date=True)

        right = fpt.Get_Price_History(
            stock=input_symbol, start_date=input_start_date, end_date=input_end_date,
            ignore_date=False, adjust_price=True, show_weekday=False, double_date=True)

        left['all_buy_R_volume'] = left['Vol_Buy_R'] - left['Vol_Sell_R']
        left = left[['Date', 'Weekday', 'all_buy_R_volume']]

        right = right[['Date', 'Adj Final']]
        right.rename(columns={'Adj Final': 'Final'}, inplace=True)

        result = left.join(right.set_index('Date'), on='Date')

        # convert to toman
        result['all_buy_R_value'] = ((result['all_buy_R_volume'] * result['Final']) / 10).round(0)
        result.reset_index(inplace=True)
        result.rename(columns={'J-Date': 'JalaliDate'}, inplace=True)

        print(result)

        context = {
            'instruments': instruments,
            'symbol_input': input_symbol,
            'start_date_input': input_start_date,
            'end_date_input': input_end_date,
            'table_data': result.to_dict('record'),
            'chart_data_date': json.dumps(result.JalaliDate.to_list()),
            'chart_data_values': json.dumps(result.all_buy_R_value.to_list()),
            'chart_data_close_price': json.dumps(result.Final.to_list()),
            'incoming_and_outgoing_differences': round(result.all_buy_R_value.sum()/1e9, 2),
        }

        return render(request, 'retail_trades_history.html', context)