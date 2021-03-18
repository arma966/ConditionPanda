from influxdb_client import InfluxDBClient

token = "mytoken"
client = InfluxDBClient(url="http://localhost:8086", token=token)

# client.switch_database('Prova')

query_api = client.query_api()

query = 'from(bucket: "Prova")\
  |> range(start: 2021-03-03T21:09:00.000Z, stop: 2021-03-04T10:00:00.000Z)\
  |> filter(fn: (r) => r["_measurement"] == "LattePanda")\
  |> filter(fn: (r) => r["Machine"] == "Motor1")\
  |> filter(fn: (r) => r["Sensor"] == "Acc1")\
  |> filter(fn: (r) => r["_field"] == "RMS") '
  
result = client.query_api().query(org="myorg", query=query)

results = []
for table in result:
    for record in table.records:
        results.append((record.get_value(), record.get_field()))

print(results)