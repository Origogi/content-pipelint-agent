from crewai.flow.flow import Flow, listen, start, router, and_, or_
from pydantic import BaseModel


class ContentPipelineState(BaseModel):

    # Input
    content_type : str = ""
    topic : str = ""

    # Internal
    max_length : int = 0
    


class ContentPipelineFlow(Flow[ContentPipelineState]):

    @start()
    def init_content_pipeline(self):
        print(self.state.content_type)
        print(self.state.topic)

        if self.state.content_type not in ["blog", "tweet", "linkedin"]:
            raise ValueError("Unsupported content type")
        

        if self.state.content_type == "tweet":
            self.state.max_length = 150
        elif self.state.content_type == "linkedin":
            self.state.max_length = 500
        else:
            self.state.max_length = 800
        

    @listen(init_content_pipeline)
    def conduct_research(self):
        print("Researching..")
        return True
    
    @router(conduct_research)
    def router(self):
        if self.state.content_type == "blog":
            return "make_blog"
        elif self.state.content_type == "tweet":
            return "make_tweet"
        else:
            return "make_linkedin"
        
    @listen("make_blog")
    def handle_make_blog(self):
        print(f"Creating a blog on {self.state.topic} with max length {self.state.max_length}")
    
    @listen("make_tweet")
    def handle_make_tweet(self):
        print(f"Creating a tweet on {self.state.topic} with max length {self.state.max_length}")
    
    @listen("make_linkedin")
    def handle_make_linkedin(self):
        print(f"Creating a linkedin post on {self.state.topic} with max length {self.state.max_length}")

    @listen(or_(handle_make_tweet, handle_make_linkedin))
    def check_varality(self):
        print("Checking validity..")

    @listen(handle_make_blog)
    def check_seo(self):
        print("Checking SEO..")   

    @listen(or_(check_varality, check_seo))
    def finalize_content(self):
        print("Finalizing content..")   
    
    
flow = ContentPipelineFlow()

flow.plot()

# flow.kickoff(
#     inputs={
#         "content_type": "tweet",
#         "topic": "AI"
#     }
# )