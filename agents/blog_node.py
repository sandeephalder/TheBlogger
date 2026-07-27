from blueprint.states.blogstate import BlogState
from prompts.questions_prompt import questions_prompt
from prompts.blogger_prompt import blogger_prompt

class BlogNode:
    """
    A class to represent he blog node
    """

    def __init__(self,llm):
        self.llm=llm

    
    def questions_breakdown(self,state:BlogState):
        """
        Break Down the question based on topic and generate a list of questions
        """
        print(" Inside Question Breakdown Node\n ===============> \n",state["topic"])
        if "topic" in state and state["topic"]:
            prompt=questions_prompt.format(topic=state["topic"])
            
            sytem_message=prompt
            print(sytem_message)
            response=self.llm.invoke(sytem_message)
            print(response)
            return {"blog":{"title":response.content}}
        
    def blog_content_generation(self,state:BlogState):
        """
        Generate blog content based on the topic
        """
        print(" Inside Blog Content Generation Node\n ===============> \n",state["blog"])
        if "topic" in state and state["topic"]:
            system_prompt =blogger_prompt
            system_message = system_prompt.format(topic=state["topic"])
            response = self.llm.invoke(system_message)
            print("Blog Content: \n ===============> \n",response.content)
            return {"blog": {"title": state['blog']['title'], "content": response.content}}


    def wordpress_blog_writer(self,state:BlogState):
        """
        Generate wiki content based on the topic
        """

        print(" Inside Wordpress Blog Writer Node\n ===============> \n",state["blog"])

        return {"blog": {"title": state['blog']['title'], "content": state['blog']['content'], "wordpress": "Wordpress Content"}}

        