# Multi Question Answer bot

This application is a Flask endpoint, exposing a single endpoint "/" which takes in 2 documents "questions" and "document" and answers all questions in the former text and answers based on the later.

Return is a JSON

## Solution 
The solution uses LangChain components like content loaders, splitters and chains along with FAISS vector database to run this application.

### Steps taken by the code to compute the answers -
1. Read json or pdf files.
2. Break down and store content document in vector DB
3. Run question answer chain over the questions, they run parallelly
4. Return the json

### Input documents -
Accepted formats are pdf and json only. You can mix file types, example questions can be json and content document can be PDF.

#### Questions 
JSON structure should be as follows -
```json
{
    "questions": [
        {
            "content": "What is the candidates name?"
        },
        {
            "content": "What is his experience with Python"
        }
    ]
}
```

PDF should have the questions start with their question numbers. There should be no additional text in between the questions or after it. Check "misc/questions.pdf" for reference

#### Content
JSON structure should be as follows -
```json
{
    "content": "Lorem Ipsum"
}
```

PDF is read as text, no specific formatting is required.

### Result 
Result is a JSON in the following format -
```json
{
	"result": [
		{
			"questions": "What is the candidates name?",
			"answer": "Khush Chopra"
		}
	]
}
```

## Running the application
1. Add OPEN API key to vars_example.py and rename it vars.py
2. Install dependencies - pip install -r requirements.txt 
3. Run application using - python main.py 

## DEMO Video






