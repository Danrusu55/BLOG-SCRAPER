import json
from watson_developer_cloud import NaturalLanguageUnderstandingV1
import watson_developer_cloud.natural_language_understanding.features.v1 \
  as Features

natural_language_understanding = NaturalLanguageUnderstandingV1(
  username="06bab10b-2043-4f98-aa79-a62aa9ed0753",
  password="cc0zAHTJpzUQ",
  version="2017-02-27")

response = natural_language_understanding.analyze(
  text='Ajar Productions Blog Blog of the 2-D animation studio dedicated to creating entertaining animation, games, and motion design. Includes posts on books, Flash, contests, extension, drawing, interviews, tips, and tutorials.',
  features=[
    Features.Keywords(
      # Keywords options
      sentiment=False,
      emotion=False,
      limit=2
    )
  ]
)

for keyword in response['keywords']:
  print(keyword['text'])

#print(json.dumps(response, indent=2))