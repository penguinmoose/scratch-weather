import scratchattach as sa
with open("secret.txt", "r") as f:
    r = f.read().splitlines()

session = sa.login(r[0], r[1])
conn = session.connect_cloud("830536684")

conn.set_vars({
    "response: current": "0",
    "response: forecastbasic": "0",
    "response: forecasttemp": "0",
    "response: forecastwind": "0",
    "response: forecastprecip": "0",
    "response: forecastastro": "0",
    "response: forecastother": "0",
    "request": "0",
    "404?": "2", # reuse 404 error to let client know that server encountered an error
})