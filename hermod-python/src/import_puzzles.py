import puz
from bs4 import BeautifulSoup
    
import uuid
import requests
from bson.objectid import ObjectId
import types  
import json
import motor
import motor.motor_asyncio
import os
import time
import sys
import asyncio
from metaphone import doublemetaphone
from string import ascii_lowercase
# DESTINATION FORMAT (FOR REACT-CROSSWORD)
# {
        # "across" : {
            # "1" : {
                # "clue" : "capital of australia",
                # "answer" : "canberra",
                # "row" : 0,
                # "col" : 0
            # },


  
        
def mongo_connect(collection):
    # logger = logging.getLogger(__name__)
    # logger.debug('MONGO CONNECT ')
    # logger.debug(str(os.environ.get('MONGO_CONNECTION_STRING')))
    
    client = motor.motor_asyncio.AsyncIOMotorClient(os.environ.get('MONGO_CONNECTION_STRING'))

    db = client['hermod']
    collection = db[collection]
    return collection


      
async def get_crossword(uid):
    print('CROSSWORD')
    print(uid)
    if uid:
        # crosswordId = None #request.getid
        # print([crosswordId])
        try:
            # print('FIND FACT conn')
            
            collection = mongo_connect('crosswords') 
            print('FIND FACT CONNECTED')
            query = {'_id':ObjectId(uid)}
            # print(query)
            document = await collection.find_one(query)
            # crosswords = []
            # async for document in collection.find(query):
                # print(document)
                # crosswords.append(document)
            # #document = await collection.find_many(query)
            # print(document)
            document['_id'] = str(document.get('_id'))
            return document
        except:
            print('FIND FACT ERR')
            e = sys.exc_info()
            print(e)  
            
            

async def save_crossword(crossword):
    
    try:
        if crossword: 
            collection = mongo_connect('crosswords') 
            # does fact already exist and need update ?
            # query = {'$and':[{'attribute':attribute},{'thing':thing}]}
            # # logger.debug(query)
            # document = await collection.find_one(query)
            # # logger.debug(document)
            # if document:
                # # logger.debug('FOUND DOCUMENT MATCH')
                # document['answer'] = answer
                # site_parts = site.split('_')
                # username = '_'.join(site_parts[:-1])
                # document['user'] = username
                # document['updated'] = time.time()
                # result = await collection.replace_one({"_id":document.get('_id')},document)
                # #logger.debug(result)
            # else:
                # logger.debug('SAVE FACT not found')
            
            crossword['created'] = time.time()
            crossword['updated'] = time.time()
            result = await collection.insert_one(crossword)
                # logger.debug('result %s' % repr(result.inserted_id))
    except:
        print('SAVE CROSSWORD ERR')
        e = sys.exc_info()
        print(e)
            
async def import_puz(data_in,link,url):
    data={"across":{}, "down":{}}    
    #puzzle = f.read('beans.puz')
    # link='../src/beans.puz'
    p = puz.load(data_in)
    numbering = p.clue_numbering()
    # print(numbering.across) 
    # print('GRID')   
    # print([p.width,p.height])   
    # print([numbering.width,numbering.height])   
    # print ('Across')
    for clue in numbering.across:
        answer = ''.join(
            p.solution[clue['cell'] + i]
            for i in range(clue['len']))
        #print (clue['num'], clue['clue'], '-', answer)
        # print (clue)
        row = clue['cell'] // (numbering.width-1) 
        col = clue['cell'] % numbering.width 
        data["across"][str(clue['num'])] = {"clue":clue['clue'],"answer":answer.lower(),"row":row,"col":col}

    for clue in numbering.down:
        answer = ''.join(
        p.solution[clue['cell'] + i * numbering.width]
        for i in range(clue['len']))
        #print (clue['num'], clue['clue'], '-', answer)
        # print (clue)
        row = clue['cell'] // (numbering.width-1) 
        col = clue['cell'] % numbering.width 
        data["down"][str(clue['num'])] = {"clue":clue['clue'],"answer":answer.lower(),"row":row,"col":col}
    # print(data["across"])
    # print("=================================================")
    # print(data["down"])
    
    final = {
      "import_id":uuid.uuid4().hex,
      "title":p.title,
      "author":p.author,
      "copyright":p.copyright,
      "copyright_link":url,
      "data":data,
      "difficulty":2,
      "country":"US",
      "link":link
    }
    await save_crossword(final)
    print("==================SAVED===============================")
    
    
async def run():
    await scrape('https://web.archive.org/web/20191017043942/http://www.macnamarasband.com/dlpuz.html')
    
async def scrape(url):
    url_parts = url.split('/')
    clean_url = "/".join(url_parts[:-1])
    print(clean_url)
    response = requests.get(url)
    links_page = response.text
    soup = BeautifulSoup(links_page, "html.parser")
    a=1000
    for link in soup.find_all('a'):
        if a <= 0:
            break;
        final_link = link.get('href')
        # print(link.get('href'))
        # relative links
        if not link.get('href').startswith('http://') and not link.get('href').startswith('https://') :
            final_link = clean_url + '/' + link.get('href')
            # print(final_link)
        
        # href=link.get('href')
        if final_link.endswith('.puz'):
            response = requests.get(final_link)
            # print(response.text)
            try :
                await import_puz(response.content,final_link,url)
            except Exception as e:
                print(e)
                pass
            a = a - 1
        
          
    
asyncio.run(run())  
    
# print ('Down')
# for clue in numbering.down:
    # answer = ''.join(
        # p.solution[clue['cell'] + i * numbering.width]
        # for i in range(clue['len']))
    # print (clue['num'], clue['clue'], '-', answer)

# print('GRID')    
# for row in range(p.height):
    # cell = row * p.width
    # # Substitute p.solution for p.fill to print the answers
    # print (' '.join(p.fill[cell:cell + p.width])    )
    

# async def run():
    # #pass
    # # only import if database is empty
    # already_imported = await is_already_imported()
    # if not already_imported:
        # collection = mongo_connect() 
        # await  import_files(collection)


# async def import_files(collection):
    # limit = 5000000000000
    # wordset_path = '/app/wordset-dictionary/data/'
    # for c in ascii_lowercase:
        # print(c)
        # if limit <=0:
            # break
        # f = open("{}{}.json".format(wordset_path,c), "r")
        # words = json.loads(f.read())
        # for word in words:
            # if limit <=0:
                # break
            # # print(word)
            # # print('=================================')
            # # print(words.get(word))
            # await save_word(collection,word,words.get(word))
            # limit = limit - 1



# ## DATABASE FUNCTIONS


# def mongo_connect():
    # print('MONGO CONNECT ')
    # print(str(os.environ.get('MONGO_CONNECTION_STRING')))
    
    # client = motor.motor_asyncio.AsyncIOMotorClient(os.environ.get('MONGO_CONNECTION_STRING'))

    # db = client['hermod']
    # collection = db['crosswords']
    # return collection



# async def is_already_imported():
    # try:
        # collection = mongo_connect() 
        # document = await collection.find_one({})
        # if document:
            # return True
        # else:
            # return False
    # except:
        # print('FIND FACT ERR')
        # e = sys.exc_info()
        # print(e)
    

# async def save_word(collection,word,data):
    
    # # print('SAVE')
    # # print([data])
    # try:
        # metaname = doublemetaphone(word)
        # queryname = metaname[0]+metaname[1]

        # clean_meanings = []
        # for meaning in data.get('meanings',[]):
            # if meaning.get('def',False):
                # clean_meanings.append({'def':meaning.get('def'),'speech_part':meaning.get('speech_part',None),'synonyms':meaning.get('synonyms',None)})
        # document = {'word': word,'meanings':clean_meanings,'_s_word':queryname}
        # await collection.insert_one(document)
    # except:
        # print('SAVE ERR')
        # e = sys.exc_info()
        # print(e)


# # async def find_fact(attribute,thing):
    
    # # print('FIND FACT')
    # # print([attribute,thing])
    # # try:
        # # print('FIND FACT conn')
        
        # # collection = mongo_connect() 
        # # print('FIND FACT CONNECTED')
        # # query = {'$and':[{'attribute':attribute},{'thing':thing}]}
        # # print(query)
        # # document = await collection.find_one(query)
        # # print(document)
        # # if document:
            # # return document
        # # else:
            # # return None
    # # except:
        # # print('FIND FACT ERR')
        # # e = sys.exc_info()
        # # print(e)
    



