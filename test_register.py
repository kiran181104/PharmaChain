import requests

payload = {
  'batchId': 'BATCH2000',
  'drugName': 'Paracetamol 500mg',
  'composition': {
    'ingredients': [
      {'name': 'Paracetamol', 'quantity': '500mg', 'percentage': 50},
      {'name': 'Microcrystalline Cellulose', 'quantity': '200mg', 'percentage': 20},
      {'name': 'Starch', 'quantity': '150mg', 'percentage': 15},
      {'name': 'Magnesium Stearate', 'quantity': '100mg', 'percentage': 10},
      {'name': 'Povidone', 'quantity': '50mg', 'percentage': 5}
    ]
  },
  'manufactureDate': 1700000000,
  'expiryDate': 1800000000,
  'manufacturerAddress': '0x992e98ff8098a6b23e96e8b8b2a49ddc020264c34580362bc3a2d406cf13577e'
}

r = requests.post('http://localhost:8000/api/drugs/register', json=payload)
print('status', r.status_code)
print('body', r.text)
