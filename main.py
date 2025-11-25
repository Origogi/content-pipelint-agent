from crewai.flow.flow import Flow, listen, start, router, and_, or_
from crewai.agent import Agent
from crewai import LLM
from pydantic import BaseModel
from tools import web_search_tool
from seo_crew import SeoCrew
from virality_crew import ViralityCrew


class BlogPost(BaseModel):
    title : str
    subtitle : str
    sections : list[str]

class Score(BaseModel):
    value : int
    reason : str

class Tweet(BaseModel):
    content : str
    hashtags : str

class LinkedInPost(BaseModel):
    hook :str
    content : str
    call_to_action : str


class ContentPipelineState(BaseModel):

    # Inputs
    content_type: str = ""
    topic: str = ""
    llm_provider: str = "gemini"  # "openai" or "gemini"

    # Internal
    max_length: int = 0
    score: Score | None = None
    research : str = ""

    # Content
    blog_post: BlogPost | None = None
    tweet: Tweet | None = None
    linkedin_post: LinkedInPost | None = None


class ContentPipelineFlow(Flow[ContentPipelineState]):

    @start()
    def init_content_pipeline(self):

        if self.state.content_type not in ["tweet", "blog", "linkedin"]:
            raise ValueError("The content type is wrong.")

        if self.state.topic == "":
            raise ValueError("The topic can't be blank.")

        if self.state.content_type == "tweet":
            self.state.max_length = 150
        elif self.state.content_type == "blog":
            self.state.max_length = 800
        elif self.state.content_type == "linkedin":
            self.state.max_length = 500

    @listen(init_content_pipeline)
    def conduct_research(self):
    
        reseacher = Agent(
            role="Head Researcher",
            backstory="You're like a digital detective who loves digging up fascinating facts and insights. You have a knack for finding good stuff that others miss,",
            goal = f"Find the most interesting and usefu info about {self.state.topic}",
            tools=[web_search_tool]
        )

        self.state.research = reseacher.kickoff(
            f"Find the most interesting and usefu info about {self.state.topic}"
        )

        return True

    @router(conduct_research)
    def conduct_research_router(self):
        content_type = self.state.content_type

        if content_type == "blog":
            return "make_blog"
        elif content_type == "tweet":
            return "make_tweet"
        else:
            return "make_linkedin_post"

    @listen(or_("make_blog", "remake_blog"))
    def handle_make_blog(self):
        blog_post = self.state.blog_post

        # Select LLM based on provider
        if self.state.llm_provider == "openai":
            llm = LLM(model="openai/gpt-4o")
        else:
            llm = LLM(model="gemini/gemini-2.0-flash-exp")

        if blog_post:
            prompt = f"""
                You wrote this blog post on {self.state.topic}, but it does not have a good SEO score
                because of {self.state.score.reason}

                Improve it
                <blog post>
                {self.state.blog_post.model_dump_json()}
                </blog post>

                Use the following research:
                <research>
                ==================
                {self.state.research}
                ==================
                </research>

                Create an improved blog post.
            """
        else:
            prompt = f"""
                Make a blog post with SEO practices on the topic {self.state.topic} using the following research:

                <research>
                ==================
                {self.state.research}
                ==================
                </research>
            """

        result = llm.call(prompt, response_model=BlogPost)
        if isinstance(result, str):
            self.state.blog_post = BlogPost.model_validate_json(result)
        else:
            self.state.blog_post = result     

    @listen(or_("make_tweet", "remake_tweet"))
    def handle_make_tweet(self):
        tweet = self.state.tweet

        # Select LLM based on provider
        if self.state.llm_provider == "openai":
            llm = LLM(model="openai/gpt-4o")
        else:
            llm = LLM(model="gemini/gemini-2.0-flash-exp")

        if tweet:
            prompt = f"""
                You wrote this tweet on {self.state.topic}, but it does not have a good viral score
                because of {self.state.score.reason}

                Improve it
                <tweet>
                {self.state.tweet.model_dump_json()}
                </tweet>

                Use the following research:
                <research>
                ==================
                {self.state.research}
                ==================
                </research>

                Create an improved tweet.
            """
        else:
            prompt = f"""
                Make a tweet that a can go viral on the topic {self.state.topic} using the following research:

                <research>
                ==================
                {self.state.research}
                ==================
                </research>
            """

        result = llm.call(prompt, response_model=Tweet)
        if isinstance(result, str):
            self.state.tweet = Tweet.model_validate_json(result)
        else:
            self.state.tweet = result 

    @listen(or_("make_linkedin_post", "remake_linkedin_post"))
    def handle_make_linkedin_post(self):
        linkedin_post = self.state.linkedin_post

        # Select LLM based on provider
        if self.state.llm_provider == "openai":
            llm = LLM(model="openai/gpt-4o")
        else:
            llm = LLM(model="gemini/gemini-2.0-flash-exp")

        if linkedin_post:
            prompt = f"""
                You wrote this linkedin post on {self.state.topic}, but it does not have a good viral score
                because of {self.state.score.reason}

                Improve it
                <linkedin post>
                {self.state.linkedin_post.model_dump_json()}
                </linkedin post>

                Use the following research:
                <research>
                ==================
                {self.state.research}
                ==================
                </research>
            """
        else:
            prompt = f"""
                Make a linkedin post that can go viral on the topic {self.state.topic} using the following research:

                <research>
                ==================
                {self.state.research}
                ==================
                </research>
            """

        result = llm.call(prompt, response_model=LinkedInPost)
        if isinstance(result, str):
            self.state.linkedin_post = LinkedInPost.model_validate_json(result)
        else:
            self.state.linkedin_post = result 


    @listen(handle_make_blog)
    def check_seo(self):
        result = (
            SeoCrew()
            .crew()
            .kickoff(
                inputs={
                    "topic": self.state.topic,
                    "blog_post": self.state.blog_post.model_dump_json(indent=2),
                }
            )
        )

        self.state.score = result.pydantic

    @listen(or_(handle_make_tweet, handle_make_linkedin_post))
    def check_virality(self):
        content = (
            self.state.tweet.model_dump_json(indent=2)
            if self.state.content_type == "tweet"
            else self.state.linkedin_post.model_dump_json(indent=2)
        )

        result = (
            ViralityCrew()
            .crew()
            .kickoff(
                inputs={
                    "topic": self.state.topic,
                    "content_type": self.state.content_type,
                    "content": content,
                }
            )
        )

        self.state.score = result.pydantic

    @router(or_(check_seo, check_virality))
    def score_router(self):

        content_type = self.state.content_type
        score = self.state.score

        print("Score: ", score)

        if score.value >=7:
            return "check_passed"

        if content_type == "blog":
            return "remake_blog"
        elif content_type == "linkedin":
            return "remake_linkedin_post"
        else:
            return "remake_tweet"

    @listen("check_passed")
    def finalize_content(self):
        print("Finalizing content")
        print("==================")
        print(self.state.blog_post)
        print(self.state.tweet)
        print(self.state.linkedin_post)


flow = ContentPipelineFlow()

flow.kickoff(
    inputs={
        "content_type": "blog",
        "topic": "xenoblade 2",
        "llm_provider": "openai",  # "openai" or "gemini"
    },
)
