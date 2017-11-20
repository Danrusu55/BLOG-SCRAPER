import nltk, re
from nltk.corpus import stopwords

with open('text.txt') as file:
    text = file.read()
    text = re.sub(r'\n',' ',text)
    text = re.sub(r'https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)','',text) #urls
    text = re.sub(r'[-/]',' ',text) # replace these with space
    text = re.sub(r'[^A-Za-z\s]','',text) # Non letters
    text = re.sub(r'[\w-]+@([\w-]+\.)+[\w-]+','',text) #emails
    text = re.sub(r'@[a-zA-Z0-9]+','',text) # handles
    tokens = [t for t in text.split()]
    clean_tokens = tokens[:]
    sr = stopwords.words('english')
    for token in tokens:
        if token in stopwords.words('english'):
            clean_tokens.remove(token)
    str = ' '.join(clean_tokens)

with open('text_out.txt',mode='w') as outFile:
    outFile.write(str)