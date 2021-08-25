
def lambda_handler(event, content):
  age = event['age'] * 10

  return {
      "name": event['name'],
      "age": age
  }
