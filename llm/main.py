from llm import LLM

if __name__ == "__main__":
    llm = LLM()
    result = llm.chat("介绍一下三国演义中的陈登")
    print(result)
