from influxdb import InfluxDBClient

influx_client = InfluxDBClient(host='localhost', port=8086)
influx_client.switch_database('bitcoin_prices')