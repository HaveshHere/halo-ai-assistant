from agent import HaloAgent
from tools.env_file import load_env_file


def main():
    load_env_file()
    agent = HaloAgent("data/tasks.txt")

    print("Halo")
    print("Ask me about your work.")
    print("Type 'exit' to quit.")

    while True:
        question = input("\nYour question: ")

        if question.lower() == "exit":
            print("Goodbye!")
            break

        answer = agent.answer(question)
        print(f"\n{answer}")


if __name__ == "__main__":
    main()
