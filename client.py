import requests

server = 'http://localhost:8000'
endpoints = ['/listSpecies?json=1', '/listSpecies?limit=10&json=1', '/listSpecies?limit=0&json=1',
             '/listSpecies?limit=wrong&json=1', '/listSpecies?limit=-2&json=1',
             '/listSpecies?limit=&json=1', '/karyotype?specie=mouse&json=1',
             '/karyotype?specie=wrong&json=1', '/karyotype?specie=homo+sapiens&json=1',
             '/chromosomeLength?specie=mouse&chromo=18&json=1', '/chromosomeLength?specie=homo+sapiens&chromo=18&json=1',
             '/chromosomeLength?specie=wrong&chromo=18&json=1',
             '/chromosomeLength?specie=mouse&chromo=wrong&json=1',
             '/geneSeq?gene=FRAT1&json=1','/geneSeq?gene=wrong&json=1',
             '/geneInfo?gene=FRAT1&json=1', '/geneInfo?gene=wrong&json=1',
             '/geneCalc?gene=FRAT1&json=1', '/geneCalc?gene=wrong&json=1',
             '/geneList?chromo=1&start=0&end=30000&json=1', '/geneList?chromo=1&start=wrong&end=30000&json=1',
             '/geneList?chromo=1&start=0&end=wrong&json=1', '/geneList?chromo=wrong&start=0&end=wrong&json=1']

for ENDPOINT in endpoints:
    r = requests.get(server + ENDPOINT, headers={"Content-Type": "application/json"})
    decoded = r.json()
    print(decoded)
