import openai
import json
import requests
import random


#wordpress credentials / jwt token
site_url = 'https://site.url/wp-json/v2/posts'
username = 'username'
password = 'password'
jwt_token = "jwt_token"

#scrapes top US headlines and selects a random one. Headline categories / country can be changed:  https://newsapi.org/docs

def headlines():
    headline_list = []
    news = requests.get('https://newsapi.org/v2/top-headlines?country=us&apiKey=api_key')
    content = news.json()
    articles = content['articles']
    for article in articles:
        title = article['title']
        first_field = title.split('-')[0].strip()
        headline_list.append(first_field)
    return(random.choice(headline_list))


#uses openai to generate a blog post based on the headline text
def airesult():
    openapi_api_key = 'openapi_api_key'
    prompt = f"In your own words, create a blog post about the following topic: {headlines()}"
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=2000,
        n=3,
        stop=None,
        temperature=0.9,
    )

    result = response.choices[0].text
    result_lines = result.split("\n")[1:]
    result_without_first_line = "\n".join(result_lines)
    return result_without_first_line

def post_to_wordpress(title, content):
     # Authenticate with the WordPress site using basic authentication to obtain a JWT token
    auth_response = requests.post(site_url + '/jwt-auth/v1/token', data={
        'username': username,
        'password': password
    })
    if auth_response.status_code != 200:
        print("Failed to authenticate with WordPress site")
        return
    jwt_token = auth_response.json()['token']

    # Create the headers required for JWT authentication
    headers = {
        'Authorization': 'Bearer ' + jwt_token,
        'Content-Type': 'application/json'
    }
    
    # Create the data object with the post title and content
    data = {
        'title': title,
        'content': content,
        'status': 'publish'
    }
    
    # Send a POST request to the WordPress REST API to create a new post
    response = requests.post(site_url, headers=headers, data=json.dumps(data))
    if response.status_code == 201:
        print("Post created successfully!")
    else:
        print("Failed to create post")

if __name__ == "__main__":
    title = headlines()
    content = airesult()
    post_to_wordpress(title, content)