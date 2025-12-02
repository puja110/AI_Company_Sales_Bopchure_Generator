import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from scraper import fetch_website_links, fetch_website_contents


class BrochureGenerator:
    def __init__(self, model="gpt-4o-mini"):
        """
        Initialize the Brochure Generator with OpenAI API
        
        Args:
            model: The OpenAI model to use (default: gpt-4o-mini)
        """
        load_dotenv(override=True)
        api_key = os.getenv('OPENAI_API_KEY')
        
        if not api_key or not api_key.startswith('sk-'):
            raise ValueError("Invalid or missing OPENAI_API_KEY in .env file")
        
        self.openai = OpenAI(api_key=api_key)
        self.model = model
        self.link_selection_model = "gpt-4o-mini"  # Use cheaper model for link selection
        
        self.link_system_prompt = """
You are provided with a list of links found on a webpage.
You are able to decide which of the links would be most relevant to include in a brochure about the company,
such as links to an About page, or a Company page, or Careers/Jobs pages.
You should respond in JSON as in this example:

{
    "links": [
        {"type": "about page", "url": "https://full.url/goes/here/about"},
        {"type": "careers page", "url": "https://another.full.url/careers"}
    ]
}
"""
        
        self.brochure_system_prompt = """
You are an assistant that analyzes the contents of several relevant pages from a company website
and creates a short brochure about the company for prospective customers, investors and recruits.
Respond in markdown without code blocks.
Include details of company culture, customers and careers/jobs if you have the information.
"""

    def get_links_user_prompt(self, url):
        """
        Create a user prompt for selecting relevant links
        
        Args:
            url: The website URL
            
        Returns:
            Formatted prompt string
        """
        user_prompt = f"""
Here is the list of links on the website {url} -
Please decide which of these are relevant web links for a brochure about the company, 
respond with the full https URL in JSON format.
Do not include Terms of Service, Privacy, email links.

Links (some might be relative links):

"""
        links = fetch_website_links(url)
        user_prompt += "\n".join(links)
        return user_prompt

    def select_relevant_links(self, url):
        """
        Use AI to select relevant links from a webpage
        
        Args:
            url: The website URL
            
        Returns:
            Dictionary containing relevant links
        """
        print(f"🔍 Selecting relevant links for {url}...")
        
        try:
            response = self.openai.chat.completions.create(
                model=self.link_selection_model,
                messages=[
                    {"role": "system", "content": self.link_system_prompt},
                    {"role": "user", "content": self.get_links_user_prompt(url)}
                ],
                response_format={"type": "json_object"}
            )
            
            result = response.choices[0].message.content
            links = json.loads(result)
            print(f"✅ Found {len(links.get('links', []))} relevant links")
            return links
        except Exception as e:
            print(f"❌ Error selecting links: {e}")
            return {"links": []}

    def fetch_page_and_all_relevant_links(self, url):
        """
        Fetch main page content and all relevant linked pages
        
        Args:
            url: The website URL
            
        Returns:
            Combined content string
        """
        print(f"📄 Fetching main page content...")
        contents = fetch_website_contents(url)
        relevant_links = self.select_relevant_links(url)
        
        result = f"## Landing Page:\n\n{contents}\n## Relevant Links:\n"
        
        for link in relevant_links.get('links', []):
            try:
                print(f"📄 Fetching {link['type']}: {link['url']}")
                result += f"\n\n### Link: {link['type']}\n"
                result += fetch_website_contents(link["url"])
            except Exception as e:
                print(f"⚠️  Could not fetch {link['url']}: {e}")
                continue
        
        return result

    def get_brochure_user_prompt(self, company_name, url):
        """
        Create the user prompt for brochure generation
        
        Args:
            company_name: Name of the company
            url: The website URL
            
        Returns:
            Formatted prompt string
        """
        user_prompt = f"""
You are looking at a company called: {company_name}
Here are the contents of its landing page and other relevant pages;
use this information to build a short brochure of the company in markdown without code blocks.

"""
        user_prompt += self.fetch_page_and_all_relevant_links(url)
        # Truncate if more than 15,000 characters to avoid token limits
        user_prompt = user_prompt[:15_000]
        return user_prompt

    def create_brochure(self, company_name, url):
        """
        Generate a brochure for the company (non-streaming)
        
        Args:
            company_name: Name of the company
            url: The website URL
            
        Returns:
            Generated brochure content as markdown string
        """
        print(f"\n🎨 Generating brochure for {company_name}...\n")
        
        try:
            response = self.openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.brochure_system_prompt},
                    {"role": "user", "content": self.get_brochure_user_prompt(company_name, url)}
                ],
            )
            
            result = response.choices[0].message.content
            print("\n✅ Brochure generated successfully!\n")
            return result
        except Exception as e:
            print(f"\n❌ Error generating brochure: {e}\n")
            return None

    def stream_brochure(self, company_name, url):
        """
        Generate a brochure with streaming output (typewriter effect)
        
        Args:
            company_name: Name of the company
            url: The website URL
            
        Yields:
            Chunks of the generated brochure
        """
        print(f"\n🎨 Generating brochure for {company_name}...\n")
        print("-" * 80)
        
        try:
            stream = self.openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.brochure_system_prompt},
                    {"role": "user", "content": self.get_brochure_user_prompt(company_name, url)}
                ],
                stream=True
            )
            
            full_response = ""
            for chunk in stream:
                content = chunk.choices[0].delta.content or ''
                full_response += content
                print(content, end='', flush=True)
                yield content
            
            print("\n" + "-" * 80)
            print("\n✅ Brochure generated successfully!\n")
            return full_response
            
        except Exception as e:
            print(f"\n❌ Error generating brochure: {e}\n")
            return None

    def save_brochure(self, brochure_content, filename):
        """
        Save brochure content to a file
        
        Args:
            brochure_content: The brochure markdown content
            filename: Output filename
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(brochure_content)
            print(f"💾 Brochure saved to {filename}")
        except Exception as e:
            print(f"❌ Error saving brochure: {e}")