from crewai.flow.flow import Flow, listen, start, router, and_, or_
from pydantic import BaseModel

class MyState(BaseModel):
    user_id : int = 1
    is_admin : bool = False

class MyFirstFlow(Flow[MyState]):

    @start()
    def first(self):
        print(self.state.user_id)
        print("Hello, World!")
        return "first_done"


    @listen(first)
    def second(self):
        print("This is the second step after the first.")
        return "second_done"

    @listen(first)
    def third(self):
        print("This is the third step after the first.")
        return "third_done"

    @listen(and_(second, third))
    def final(self):
        print("All steps completed!")
        self.state.user_id = 100
        return "all_done"
    
    @router(final)
    def route(self):
        a = 2

        if a % 2 == 0:
            return "even"
        else:
            return "odd"
        
    
    @listen('even')
    def even_path(self):
        print(self.state.user_id)

        print("The number is even.")

    @listen('odd')
    def odd_path(self):
        print("The number is odd.")


flow = MyFirstFlow()

# flow.plot()

result = flow.kickoff()
print(f"\nFlow result: {result}")

