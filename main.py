from crewai.flow.flow import Flow, listen, start, router, and_, or_

class MyFirstFlow(Flow):

    @start()
    def first(self):
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
        return "all_done"

flow = MyFirstFlow()

flow.plot()

result = flow.kickoff()
print(f"\nFlow result: {result}")

