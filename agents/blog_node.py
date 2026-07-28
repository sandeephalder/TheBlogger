from blueprint.states.blogstate import BlogState
from prompts.questions_prompt import questions_prompt
from prompts.blogger_prompt import blogger_prompt
from utils.colors import print_cyan, print_green, print_magenta, print_blue

class BlogNode:
    """
    A class to represent the blog node
    """

    def __init__(self, llm):
        self.llm = llm

    def questions_breakdown(self, state: BlogState):
        """
        Break Down the question based on topic and generate a list of questions
        """
        print_cyan(f"\n🔍 Inside Question Breakdown Node\n ===============> \nTopic: {state['topic']}")
        if "topic" in state and state["topic"]:
            prompt = questions_prompt.format(topic=state["topic"])
            system_message = prompt
            print_blue(f"System Message:\n{system_message}")
            response = self.llm.invoke(system_message)
            print_cyan(f"Question Breakdown Response:\n{response.content}")
            return {"blog": {"title": response.content}}

    def blog_content_generation(self, state: BlogState):
        """
        Generate blog content based on the topic
        """
        print_green(f"\n✍️  Inside Blog Content Generation Node\n ===============> \nBlog State: {state['blog']}")
        if "topic" in state and state["topic"]:
            system_prompt = blogger_prompt
            system_message = system_prompt.format(topic=state["topic"])
            response = self.llm.invoke(system_message)
            print_green(f"\n✨ Generated Blog Content:\n ===============> \n{response.content}")
            return {"blog": {"title": state['blog']['title'], "content": response.content}}

    def wordpress_blog_writer(self, state: BlogState):
        """
        Generate wiki content based on the topic
        """
        print_magenta(f"\n🌐 Inside Wordpress Blog Writer Node\n ===============> \nBlog State: {state['blog']}")
        return {"blog": {"title": state['blog']['title'], "content": state['blog']['content'], "wordpress": "Wordpress Content"}}