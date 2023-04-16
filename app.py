import openai
import requests
import streamlit as st

# Function to fetch data from GitHub
def fetch_github_data(technology):
    url = f"https://api.github.com/search/repositories?q={technology}+in:name+in:description+in:topics+in:readme&per_page=100"
    response = requests.get(url)
    results = response.json()
    return results

# Streamlit app
st.title("Find Developers on Github Matching Your Job Description")
st.write("Enter the job description below to find devs that best match your job description.")

job_description = st.text_area("Job description", height=400)

if st.button("Submit"):
    openai.api_key = "API_KEY"

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"Extract the name of programming languages and/or libraries mentioned in the following job description. Do not include technological skills like in the list even if asked for. :\n{job_description}"}],
        temperature=0,
    )

    technologies = response['choices'][0]['message']['content'].split(", ")
    technologies = dict.fromkeys(technologies)

    for technology in technologies:
        technologies[technology] = fetch_github_data(technology)

    min_total_count = float('inf')
    min_technology = None

    for technology in technologies:
        total_count = technologies[technology]['total_count']
        if total_count < min_total_count:
            min_total_count = total_count
            min_technology = technology

    owners = []
    for i in range(0, len(technologies[min_technology]["items"]), 6):
        owners += list(map(lambda item: (item["owner"]["login"], item["owner"]["html_url"]), filter(lambda item: item["owner"]["type"] == "User", technologies[min_technology]["items"][i:i+6])))

    owners = dict(owners).items()

    #st.write(f"Least popular technology: {min_technology}")
    st.write("Repository owners:")

    # Display clickable links to GitHub profiles
    for owner, url in owners:
        st.markdown(f"[{owner}]({url})")