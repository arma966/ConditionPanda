import pandas as pd
import time

# Microseconds

t = format(time.time()*1e6,'.0f')

#convert sample data to line protocol (with nanosecond precision)
df = pd.read_csv("test3.csv")
df["Time (s)"] = df["Time (s)"]*1e6 + float(t)
# df=df.astype({'Time (s)': int})

lines = ["meas"
          + ",tag1='scarico'"
          + " "
          + "acc1=" + str(format(df["AI 1 (m/s2)"][d],'.9f')) +''
          + " " + str(format(df["Time (s)"][d],'.0f'))+ '000' for d in range(60000)]




thefile = open('../influxData/test3_linep', 'w', newline="",encoding='utf8')
for item in lines:
    thefile.write("%s\n" % item)

thefile.close()
print("The end")