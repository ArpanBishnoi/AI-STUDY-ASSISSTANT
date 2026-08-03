import psycopg
import uvicorn
from enum import Enum
from prompts import SUMMARY_PROMPT,NOTES_PROMPT,EXPLAIN_PROMPT,REVISION_PROMPT,EXAM_PROMPT,QUIZ_PROMPT,FLASHCARD_PROMPT
from embedding import generate_embedding
from chroma_client import chunks_collection
from search import ask_pdf
from search import search_chunks
import fitz
#from google import genai
import uuid
from llm import generate_response
from fastapi import UploadFile,File
import shutil
from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
import bcrypt
from datetime import datetime,timedelta
from jose import jwt,JWTError
import os
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from fastapi import Depends
#client=genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
app = FastAPI()
security = HTTPBearer()
SECRET_KEY = "super_secret_key_change_later"
ALGORITHM = "HS256"
def get_current_user(credentials:HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
         payload = jwt.decode(
          token,
          SECRET_KEY,
           algorithms=ALGORITHM
           )
         user_id = payload.get("sub")
         if user_id is None:
             raise HTTPException(
                 status_code=401,
                 detail='invalid'
             )
         return user_id
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail='Invalid or expired token'
        )
def get_connection():
    return psycopg.connect(
        host = os.getenv('DB_HOST'),
        port = os.getenv('DB_PORT'),
        dbname = os.getenv('DB_NAME'),
        user = os.getenv('DB_USER'),
        password = os.getenv('DB_PASSWORD')        
        )


def add_user(username,email,password):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO users (username,email,password) VALUES (%s,%s,%s)""",(username,email,password)
    )
    conn.commit()
    cur.close()
    conn.close()
class Userinput(BaseModel):
    username : str
    email:str
    password:str
class Logininput(BaseModel):
    email : str
    password :str
@app.post('/Register')
def register_user(item:Userinput):
    hashed_password = bcrypt.hashpw(item.password.encode(),bcrypt.gensalt()).decode()
    add_user(item.username,item.email,hashed_password) 
    return{'User Registered Successfully !!'}
def get_user_by_email(email):
    conn = get_connection()
    cur = conn.cursor()      
    cur.execute('SELECT * FROM users   WHERE email = %s',(email,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user 
@app.post('/Login')
def login_user(item:Logininput):
    user = get_user_by_email(item.email)
    if user is None:
        raise HTTPException(
            status_code = 401,
            detail = 'Invalid email or password'
        )
    if not bcrypt.checkpw(item.password.encode(),user[3].encode()):
        raise HTTPException(
            status_code=401,
            detail ='Invalid email or password'
        )
    token = create_access_token(user[0])
    return{'access_token':token,
           'token_type':'bearer'}
def create_access_token(user_id):
     expire = datetime.utcnow() + timedelta(days=1)
     payload = {'sub':str(user_id), "exp": expire}
     token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
     return token
@app.get('/profile')
def profile(current_user =Depends(get_current_user)):
    return {
        'user_id':current_user
    }   
@app.post('/upload-pdf')
def upload_pdf(
    file: UploadFile = File(...),
    current_user = Depends(get_current_user)
):
      try:
          print('uploaded endpoint reached')
          os.makedirs('uploads', exist_ok=True)
          unique_filename = f'{uuid.uuid4()}_{file.filename}'
          file_path = os.path.join('uploads',unique_filename)
          with open(file_path,'wb') as buffer:
             shutil.copyfileobj(file.file,buffer)
             pdf_text = extract_text_from_pdf(file_path)
             conn =get_connection()
             cur=conn.cursor()
             cur.execute('INSERT INTO pdfs(user_id,title,file_path,content) VALUES (%s,%s,%s,%s) RETURNING id',(current_user,file.filename,file_path,pdf_text))
             pdf_id = cur.fetchone()[0]
             conn.commit()
             cur.close()
             conn.close()
             get_chunks_for_pdf(pdf_id,current_user)
             return{'message':'PDF uploaded successfully !!!'}
      except Exception as e:
            return {'error':str(e)}
def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    text = ''
    for page in doc:
        text +=page.get_text()
    doc.close() 
    return text
def get_pdf_content(pdf_id,verification_id):
    conn =get_connection()
    cur = conn.cursor()
    cur.execute('SELECT content FROM pdfs WHERE id = %s AND user_id = %s ', (pdf_id, verification_id))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row is None:
        return None
    return row[0]
def summarize_text(pdf_id,user_id):
    content = get_pdf_content(pdf_id,user_id)
    if content is None:
        raise HTTPException(
            status_code=404,
            detail='PDF not found'  
        )
    prompt = SUMMARY_PROMPT.format(content=content)
    summary = generate_response(prompt)
    return summary

#for model in client.models.list():
    #print(model.name)
     #print(model.display_name)
    #print(model.supported_actions)
    #print('---------------')
#print(summarize_text(5,6))

def get_user_pdfs(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(' SELECT id,title,uploaded_at FROM pdfs WHERE user_id =%s',(user_id,))
    pdfs = cur.fetchall()
    cur.close()
    conn.close()
    return pdfs
@app.get('/my-pdfs')
def my_pdfs(current_user = Depends(get_current_user)):    
    pdfs=get_user_pdfs(current_user)
    return{'your pdfs are':pdfs}
def get_pdf_by_id(pdf_id,user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT id,title,file_path,uploaded_at FROM pdfs WHERE id = %s AND user_id = %s',(pdf_id,user_id))
    pdf = cur.fetchone()
    cur.close()
    conn.close()
    return pdf

@app.get('/pdf/{pdf_id}')
def get_pdf(pdf_id:int,current_user = Depends(get_current_user)):
    pdf = get_pdf_by_id(pdf_id,current_user)
    return { 'here is your pdf':pdf}

def delete_pdf_by_id(pdf_id,user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT file_path FROM pdfs WHERE id = %s AND user_id = %s',(pdf_id,user_id))
    row = cur.fetchone()
    if row is None:
        raise HTTPException(
            status_code=404,
            detail='PDF not found'
        )
    os.remove(row[0])  # Delete the file from the filesystem
    cur.execute('DELETE FROM pdfs WHERE id = %s AND user_id = %s',(pdf_id,user_id))
    conn.commit()
    cur.close()
    conn.close()
@app.delete('/pdf/{pdf_id}')
def delete_pdf(pdf_id:int,current_user = Depends(get_current_user)):
    delete_pdf_by_id(pdf_id,current_user)
    return {'message':'PDF deleted successfully'}
def rename_pdf_by_id(pdf_id,user_id,new_title):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('UPDATE pdfs SET title = %s WHERE id = %s AND user_id = %s',(new_title,pdf_id,user_id))
    conn.commit()
    cur.close()
    conn.close()
@app.put('/pdf/{pdf_id}/rename')
def rename_pdf(pdf_id:int,new_title:str,current_user = Depends(get_current_user)):
    rename_pdf_by_id(pdf_id,current_user,new_title)
    return {'message':'PDF renamed successfully'}
def chunk_text(text, chunk_size=1000, overlap=200):
    chunks = []
    start = 0
    while start <len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap
    return chunks

def get_chunks_for_pdf(pdf_id,user_id):
    content= get_pdf_content(pdf_id,user_id)
    if content is None:
        return []
    chunks = chunk_text(content)
    for i,chunk in enumerate(chunks):
     embedding = generate_embedding(chunk)
     chunks_collection.add(
        ids=[f'{pdf_id}_chunk_{i}'],
        documents=[chunk],
        embeddings=[embedding],
        metadatas=[{"pdf_id":pdf_id,"user_id":user_id,"chunk_number":i}],
     )

#pdf_id = 5
#user_id = 6
#get_chunks_for_pdf(pdf_id,user_id)    
#print(chunks_collection.count())   
#exit() 

@app.put('/SUMMARIZE_PDF')
def summarize_pdf(pdf_id:int,current_user = Depends(get_current_user)):
    summary = summarize_text(pdf_id,current_user)
    return {' Your summary':summary}
class QUESTIONINPUT(BaseModel):
    pdf_id : int
    question :str
@app.post('/ASK')     
def ask_question(item: QUESTIONINPUT,current_user =Depends(get_current_user)):
     content = get_pdf_content(item.pdf_id,current_user)
     answer = ask_pdf(item.question,item.pdf_id,current_user,full_content=content)
     save_pdf(current_user,item.pdf_id,item.question,answer)
     return {'THE ANSWER OF YOUR QUESTION': answer}
def save_pdf(user_id,pdf_id,question,answer): 
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO chat_history(user_id,pdf_id,question,answer) VALUES (%s,%s,%s,%s)',(user_id,pdf_id,question,answer))
    cur.close()
    conn.commit() 
def get_chat_history(user_id,pdf_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM chat_history WHERE user_id = %s and pdf_id = %s ',(user_id,pdf_id,)) 
    rows = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return rows
@app.get('/Chat history')
def get_chat(pdf_id,current_user=Depends(get_current_user)):
    history = get_chat_history(current_user,pdf_id)
    return {'chat history ': history}
def get_notes(user_id,pdf_id):
    content = get_pdf_content(pdf_id,user_id)
    prompt = NOTES_PROMPT.format(content=content)
    notes = generate_response(prompt)
    return notes
@app.get('/GET NOTES')
def show_notes(pdf_id,current_user = Depends(get_current_user)):
    notes = get_notes(current_user,pdf_id)
    return {'Your notes are':
            notes}
def explain_pdf(question:str,user_id,pdf_id):
    content = get_pdf_content(pdf_id,user_id)
    prompt = EXPLAIN_PROMPT.format(content= content,question = question)
    explanation = generate_response(prompt)
    return explanation
class Explaininput(BaseModel):
    question :str
    pdf_id:int 

@app.post('/EXPLAIN AI')
def explain(item:Explaininput,current_user = Depends(get_current_user)):
    result = explain_pdf(item.question,current_user,item.pdf_id)
    return {'Your results are':
            result }
def revise(user_id,pdf_id):
    content = get_pdf_content(pdf_id,user_id)
    prompt = REVISION_PROMPT.format(content=content)
    result = generate_response(prompt)
    return result
@app.get('/REVISE AI')
def revision(pdf_id,current_user = Depends(get_current_user)):
    results = revise(current_user,pdf_id)
    return {'Results':results}
def generate_ques(pdf_id,user_id):
    content = get_pdf_content(pdf_id,user_id)
    prompt = EXAM_PROMPT.format(content= content)
    result = generate_response(prompt)
    return result
@app.get('/PROBABLE QUESTION BANK')
def ques(pdf_id,current_user =Depends(get_current_user)):
    questions = generate_ques(pdf_id,current_user)
    return {'Most probabable questions':
            questions}
def generate_quiz(user_id,pdf_id):
    content = get_pdf_content(pdf_id,user_id)
    prompt =QUIZ_PROMPT.format(content= content)
    result = generate_response(prompt)
    return result 
@app.get('/QUIZ_QUESTIONS')
def get_quiz(pdf_id,current_user = Depends(get_current_user)):
    quiz_questions = generate_quiz(current_user,pdf_id)
    return {'Here are your questions':quiz_questions}
class Difficulty(str , Enum):
    easy = 'Easy'
    medium = 'Medium'
    hard = 'Hard'
class Flashcardrequest(BaseModel):
    pdf_id : int
    num_flashcards : int
    difficulty: Difficulty
@app.post('/Generate_flashcard')
def flashcard(item:Flashcardrequest,current_user = Depends(get_current_user)):
    content = get_pdf_content(item.pdf_id,current_user)
    prompt =FLASHCARD_PROMPT.format(content = content,num_flashcards= item.num_flashcards,difficulty=item.difficulty)
    response = generate_response(prompt)
    return{'HERE ARE Your Flashcards': response}


