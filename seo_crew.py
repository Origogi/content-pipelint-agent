from crewai.project import CrewBase, agent, task, crew
from crewai import Agent, Task, Crew
from pydantic import BaseModel

class Score(BaseModel):
    value : int
    reason : str


@CrewBase
class SeoCrew:

    @agent
    def seo_expert(self):
        return Agent(
            role="SEO Expert",
            backstory="You are an SEO expert with a deep understanding of search engine optimization.",
            goal="Optimize content for search engines and improve its visibility in search results.",
        )

    
    @task
    def seo_audit(self):
        return Task(
            description="""
            Analaze the blog post for SEO effectiveness. and provide:


            1. An SEO score from 0 to 10 based on :
                - Keyword optimization
                - Title effectiveness
                - Content effectiveness
                - Readability
                - Search Intent alignment

            2. A clear reason explaining the score, forcusing on:
                - Main strength (if score is high)
                - Critical weakness that need improvement (if score is low)
                - The most important factor affecting the score

            Blog post to anlayze: {blog_post}
            Target topic: {topic}
            """,
            expected_output="""
            A score object with:

            - value : integer from 0 to 10
            - reason : string explaining the score  
            """,
            agent=self.seo_expert(),
            output_pydantic=Score,
        )

    @crew
    def crew(self):
        return Crew(
            agents= self.agents,
            tasks= self.tasks,
            verbose=True,   
        )