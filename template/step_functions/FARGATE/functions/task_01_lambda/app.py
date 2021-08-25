
def lambda_handler(event, content):
  result = [
    {
      "name": "name1",
      "age": 1
    },
    {
      "name": "name2",
      "age": 2
    },
    {
      "name": "name3",
      "age": 3
    }
  ]

  return {
    "list" : result,
    "stage_type": "dev"
  }
