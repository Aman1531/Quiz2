# Quiz2

This app uses FastApi for speed , scalability and developer ease 
pip install -r requirements.txt
uvicorn main:app --reload

will run the app on localhost:8000

localhost:8000/docs will open swagger docs 

by default it uses sqlite for testing which can generate error
if you visit /analytics/visual-summary route due to missing stddev function . 
please switch to postgres by uncommenting  in database.py
