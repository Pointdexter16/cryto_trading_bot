import requests
import matplotlib.pyplot as plt
import ta
import pandas as pd
from time import sleep
r=requests.get('https://financialmodelingprep.com/api/v3/historical-chart/1min/BTCUSD?apikey=0bfc95f37609fb28d97ec0b165b9c540').json()
date,close=[],[]
for i in range(1,len(r)+1):
    date.append(r[len(r)-i]['date'])
    close.append(r[len(r)-i]['close'])
raw_data={
    'date':date,
    'close':close
}
df = pd.DataFrame(raw_data)
bol = ta.volatility.BollingerBands(df['close'],window_dev=1)
df['hband']=bol.bollinger_hband()
df['lband']=bol.bollinger_lband()
df['mavg']=bol.bollinger_mavg()
df.dropna(subset=['lband'],inplace=True)    
# plt.plot(df['date'],df['close'])
# plt.plot(df['date'],df['hband'],color='orange')
# plt.plot(df['date'],df['lband'],color='orange')
# plt.plot(df['date'],df['mavg'],'g--')
# plt.fill_between(df['date'],df['lband'],df['hband'],alpha=0.2,color='orange')
df.reset_index(drop=True, inplace=True)
time=df['date'][df.shape[0]-1]
print(df)
with open("btc_log.txt",'a') as f:
    f.write(df.head(5).to_string())
    f.write("\n..........................................................................\n")
    f.write(df.tail(5).to_string(header=False))
initialization=0   
reservoir=100
invested=0
count=0
previous_status_odd=''
previous_status_even=''
status=''
price_on_buy=0
iteration='first'
while True:
    if initialization==0:
        pass
    else:
        sleep(60)
    param = {'from' : time}
    r=requests.get('https://financialmodelingprep.com/api/v3/historical-chart/1min/BTCUSD?apikey=0bfc95f37609fb28d97ec0b165b9c540',params=param).json()
    time=r[0]['date']
    close=r[0]['close']
    close_list=df['close'][df.shape[0]-500:]
    close_list.loc[len(close_list.index)] = close
    close_list.reset_index(drop=True, inplace=True)
    bol = ta.volatility.BollingerBands(close_list,window_dev=1)
    df.loc[len(df.index)] = [time,close,bol.bollinger_hband()[close_list.shape[0]-1],bol.bollinger_lband()[close_list.shape[0]-1],bol.bollinger_mavg()[close_list.shape[0]-1]]
    print(df)
    with open("btc_log.txt",'a') as f:
        f.write(f"\n\n{df.tail(5).to_string()}\n")
    # lower_tolerance=df['lband'][len(df.index)]
    # mavg_current=df['mavg'][len(df.index)]
    # upper_tolerance=df['hband'][len(df.index)]
    previous_close=df['close'][len(df.index)-2]
    if(close<previous_close):
        status='fall'
    elif(close>previous_close):
        status='climb'
    if initialization==0:
        previous_status=status
        previous_status_even=status
        initialization=1
    elif(count%2==0):
        previous_status_even=status
        previous_status=previous_status_odd
    else:
        previous_status_odd=status
        previous_status=previous_status_even
    if((previous_status!=status)or(iteration=='first')):
            if(status=='climb'):
                invested=reservoir
                reservoir=0
                price_on_buy=close
                with open("btc_log.txt",'a') as f:
                    f.write(f'stock bought at {close}\n')
                print(f'stock bought at {close}')
            elif((status=='fall' and price_on_buy!=0) and iteration!='first'):
                shift=(close-price_on_buy)/price_on_buy
                reservoir=invested+(invested*shift)
                invested=0
                price_on_buy=0
                with open("btc_log.txt",'a') as f:
                    f.write(f'stock sold at {close}\n')                
                print(f'stock sold at {close}')
            
    print("previous status:",previous_status)
    print("status :",status)
    print("reservoir :",reservoir)
    print("amount invested :",invested)
    print("price at which coin was bought :", price_on_buy)
    with open("btc_log.txt",'a') as f:
        f.write(f"previous status: {previous_status}\n")
        f.write(f"status: {status}\n")
        f.write(f"reservoir: {reservoir}\n")
        f.write(f"amount invested: {invested}\n")
        f.write(f"price at which coin was bought: {price_on_buy}\n\n" )
        f.write("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX\n\n")
    count+=1
    if(iteration=='first'):
        iteration=''
