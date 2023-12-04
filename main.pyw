import typing
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import QObject
from testui import Ui_MainWindow
import json
import sys
import drivers
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


class MyThread(QtCore.QThread):
    ThreadSignal = QtCore.pyqtSignal(dict)
    def __init__(self, func, *args,parent = None, **kwargs) -> None:
        super().__init__(parent=parent)
        self.args = args
        self.func = func
        self.kwargs = kwargs

    def run(self):
        result:dict = self.func(*self.args, **self.kwargs)
        self.ThreadSignal.emit(result)



class MyWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(MyWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.ApplyKey.clicked.connect(self.get_keys)
        self.ui.AcceptOrder.clicked.connect(self.push_order)
        self.ui.RefreshBalance.clicked.connect(self.get_balance)
        try:
            with open('keys.json', 'r+') as file:
                api_keys = json.load(file)
            if api_keys['key'] and api_keys['secret']:
                self.driver = drivers.Exmo(api_keys['key'], api_keys['secret'])
            self.get_balance()
            self.set_pairs()
            self.set_orders()
        except Exception:
            pass
        

    def get_keys(self):
        api_key = self.ui.APIKEY.text()
        api_secret = self.ui.SECRET.text()
        self.ui.APIKEY.clear(); self.ui.SECRET.clear()
        keys = dict(
            key = api_key,
            secret = api_secret
        )
        print (keys)
        with open('keys.json', 'w+') as file:
            json.dump(keys, file)
        with open('keys.json', 'r+') as file:
            api_keys = json.load(file)
        if api_keys:
            self.driver = drivers.Exmo(api_keys['key'], api_keys['secret'])
        self.set_pairs()
        self.get_balance()
        self.set_orders()


    def push_order(self):
        pair = self.ui.PairChoise.currentText()
        pair = pair.split('/')
        base = pair[0]
        quote = pair[1]
        quantity = self.ui.Quantity.text()
        type = self.ui.OrderBox.currentText()
        side = self.ui.OrderSide.currentText()
        match type, side:
            case 'Limit order', 'BUY':
                type = 'buy'
            case 'Limit order', 'SELL':
                type = 'sell'
            case 'Market order', 'BUY':
                type = 'market_buy'
            case 'Market order', 'SELL':
                type = 'market_sell'
            case 'Market order(quote)', 'BUY':
                type ='market_buy_total'
            case 'Market order(quote)', 'SELL':
                type ='market_sell_total'

        if self.ui.Price.text():
            price = self.ui.Price.text()
        else:
            price = 0
        send_order = MyThread(self.driver.order_create, base=base, quote=quote, type=type, quantity=quantity, price=price)
        send_order.ThreadSignal.connect(self.order_result); send_order.start()
        self.get_balance()
        #self.order_result(send_order)
        self.set_orders()
        

    def order_result (self, data):
        match data['result']:
            case False:
                self.ui.OrderStateLabel.setText(f'<p style = "color : rgb(250,55,55);">{data["error"].split(":")[1]}</p>')
                
            case True:
                self.ui.OrderStateLabel.setText(f'<p style = "color : rgb(55,250,55);">Sucsess</p>')

           
    def get_balance(self):
        try:
            #balances = self.driver.user_info()
            balances = self.driver.user_info()['balances']
            #print (balances)
            df = pd.DataFrame(data=balances.values(), index=balances.keys(), columns=['Val'])
            df['Val'] = pd.to_numeric(df['Val'])
            df = df[df['Val']>0]
            df = df.to_dict()
            for _ in df['Val'].keys():
                if _ not in ['USD','USDT','USDX']:
                    try:
                        r = self.driver.required_amount(_,'USDT',1)
                        if r.get('error'):
                            continue
                        df[_] = df[_] * float(r['amount'])
                    except KeyError:
                        r = self.driver.required_amount(_,'USD',1)
                        if r.get('error'):
                            continue
                        df[_] = df[_] * float(['amount'])
            df = pd.Series(df['Val'])
            df = df[df > 1]
            plt.figure(figsize=(300/96, 300/96), dpi=96)
            plt.pie(df, labels=df.index)
            plt.savefig('balances.png')
            plt.close()
            self.set_pic_balances()
            self.set_line_balaces(balances)
        except AttributeError:
            pass


    def set_pic_balances(self):
        try:
            image_balances = QtGui.QImage('balances.png')
            scene_balances = QtWidgets.QGraphicsScene()
            scene_balances.addPixmap(QtGui.QPixmap.fromImage(image_balances))
            self.ui.Balances.setScene(scene_balances)
            self.ui.Balances.show()
        except Exception:
            pass


    def set_line_balaces(self, data:dict):
        box = QtWidgets.QVBoxLayout()
        widget = QtWidgets.QWidget()
        data = sorted(data.items(), key = lambda x : x[1], reverse = True); data = dict(data)
        for key in data.keys():
            object = QtWidgets.QLabel(f'{key} : {data[key]}')
            box.addWidget(object)
        widget.setLayout(box)
        self.ui.BalancesArea.setWidget(widget)


    def set_pairs(self):
        try:
            data_pair = self.driver.pair_settings()
            data_pair = data_pair.keys()
            data_pair = tuple(map(lambda x: x.replace('_','/'), data_pair))
            for _ in data_pair:
                self.ui.PairChoise.addItem(_)
        except Exception:
            pass


    def set_orders(self):
        widget = QtWidgets.QWidget()
        data = self.driver.open_orders()
        box = QtWidgets.QVBoxLayout()
        widget_order = QtWidgets.QWidget()
        box_0 = QtWidgets.QHBoxLayout()
        for _ in ['', 'order id', 'type', 'pair', 'quantity', 'price', 'total_usd']:
            object = QtWidgets.QLabel(f'{_}')
            object.setAlignment(QtCore.Qt.AlignCenter)
            box_0.addWidget(object)
        widget_order.setLayout(box_0)
        box.addWidget(widget_order)

        for _ in data.keys():
            for order in data[_]:
                widget_order = QtWidgets.QWidget()
                box_0 = QtWidgets.QHBoxLayout()
                for j in order.keys():

                    if j in ['client_id','created']:
                        continue

                    if j == 'order_id':
                        order_id = QtWidgets.QLabel(f'{order[j]}')
                        order_id.setAlignment(QtCore.Qt.AlignCenter)
                        cancel_button = QtWidgets.QPushButton()
                        cancel_button.setText(f'Cancel order\n{order_id.text()}')
                        cancel_button.setCheckable(True)
                        box_0.addWidget(cancel_button)
                        box_0.addWidget(order_id)
                        cancel_button.clicked.connect(self.cancel_order)
                        
                    else:
                        position_0 = QtWidgets.QLabel(f'{order[j]}')
                        position_0.setAlignment(QtCore.Qt.AlignCenter)
                        box_0.addWidget(position_0)
                    
                widget_order.setLayout(box_0)
                box.addWidget(widget_order)
        box.addStretch()
        widget.setLayout(box)
        self.ui.OrdersArea.setWidget(widget)
        #self.get_balance()


    def cancel_order(self):
        sender = self.sender()
        self.driver.cancel_order(sender.text().split()[-1])
        self.set_orders()
        


if __name__ == '__main__': 
    app = QtWidgets.QApplication([])
    application = MyWindow()
    application.show()
    sys.exit(app.exec())
    
