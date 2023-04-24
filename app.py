import streamlit as st
import requests
import re
import openai

def process_job_description(job_description):
    openai.api_key = "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"

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages = [{"role": "user", "content": f"""Instructions:
                                                  Step 1) Extract formal coding languages, libraries and other technologies from this job description, listing formal coding languages first, libraries second (do not include package managers) and other technologies that are not explicitly language or libraries third. Format should be Languages, libraries, other technologies: [insert languages, libraries, other technologies]
                                                  Step 2) Reorder them in terms of most important for the job, listing them from most important to least important. Format should be Languages, libraries, other technologies: [insert languages, libraries, other technologies]
                                                  Step 3) Extract the tech stack most important for this job using the fewest number of coding languages, libraries and other technologies. Format should be Tech stack: [insert tech stack]
                                                  Step 4) Remove any coding languages from the tech stack, which are used to write any of the libraries in the tech stack. Format should be Tech stack: [insert refined tech stack]
                                                  \n{job_description}"""}],
        temperature = 0,
    )

    content = response['choices'][0]['message']['content']

    ordered_pattern = r"Languages, libraries, other technologies: (.+)"
    ordered_matches = re.findall(ordered_pattern, content)

    if len(ordered_matches) > 1:
        ordered = ordered_matches[1]
    else:
        ordered = "Not enough occurrences of the pattern found."

    refined_pattern = r"Tech stack: (.+)"
    refined_matches = re.findall(refined_pattern, content)

    if refined_matches:
        refined = refined_matches[0]
    else:
        refined = "No matches found for 'Refined tech stack'."

    ordered = re.sub(r'\s*,\s*', ',', ordered)
    refined = re.sub(r'\s*,\s*', ',', refined)
    ordered_tech_list = re.sub(r'\s*\([^)]*\)', '', ordered).split(",")
    refined_tech_list = re.sub(r'\s*\([^)]*\)', '', refined).split(",")

    return ordered_tech_list, refined_tech_list

def search_repository_owners(job_description):
    ordered_tech_list, refined_tech_list = process_job_description(job_description)

    rtl_length = len(refined_tech_list)
    url = f"https://api.github.com/search/repositories?q={refined_tech_list[0%rtl_length]}+{refined_tech_list[1%rtl_length]}+{refined_tech_list[2%rtl_length]}+NOT+list+NOT+notes+in:name+in:description+in:topics+in:readme&per_page=100"
    response = requests.get(url)
    results = response.json()

    owners = list(map(lambda item: item["owner"]["html_url"], filter(lambda item: item["owner"]["type"] == "User", results["items"])))

    return owners

# Streamlit app layout and interaction
st.title("SyntheSkills")
st.subheader("Talent search engine for software engineers")

job_description = st.text_area("Enter the job description:", value="", height=300)
search_button = st.button("Search")

if search_button:
    if job_description:
        owner_links = search_repository_owners(job_description)
        st.subheader("Results:")
        for link in owner_links:
            st.write(link)
    else:
        st.error("Please enter a job description.")
